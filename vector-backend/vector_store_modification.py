import openai
import os
import mimetypes
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import simpleSplit
import traceback
import time
import hashlib
from cache_config import cache, CacheTypes

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directories
PDF_DIR = "downloaded_pdfs"
TEXT_DIR = "site_texts"
TEMP_CONVERTED_DIR = "converted_pdfs"
os.makedirs(TEMP_CONVERTED_DIR, exist_ok=True)

# Load vector store ID
with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()

uploaded_file_ids = []

# Convert TXT file to PDF with proper wrapping
def convert_txt_to_pdf(txt_path):
    pdf_filename = os.path.splitext(os.path.basename(txt_path))[0] + ".pdf"
    pdf_path = os.path.join(TEMP_CONVERTED_DIR, pdf_filename)

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        c = canvas.Canvas(pdf_path, pagesize=LETTER)
        width, height = LETTER
        y = height - 40

        for line in lines:
            line = line.strip()
            if not line:
                continue

            wrapped_lines = simpleSplit(line, "Helvetica", 10, width - 80)
            for wrapped_line in wrapped_lines:
                c.drawString(40, y, wrapped_line)
                y -= 15
                if y < 40:
                    c.showPage()
                    y = height - 40

        c.save()
        print(f"✅ Converted: {txt_path} → {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"❌ Failed to convert {txt_path} to PDF:")
        traceback.print_exc()
        return None

def get_file_content_hash(filepath):
    """Generate hash of file content for deduplication"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        print(f"Error generating hash for {filepath}: {e}")
        return None

# Upload file to OpenAI with caching
def upload_file(filepath, retries=3):
    filename = os.path.basename(filepath)
    
    # Check if file content already uploaded
    content_hash = get_file_content_hash(filepath)
    if content_hash:
        cached_file_id = cache.get(CacheTypes.VECTOR_STORE, content_hash)
        if cached_file_id:
            print(f"📋 File content already uploaded: {filename} → ID: {cached_file_id}")
            return cached_file_id
    
    try:
        print(f"📤 Uploading: {filename} ({os.path.getsize(filepath)/1024:.1f} KB)")

        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type is None:
            mime_type = "application/octet-stream"

        for attempt in range(retries):
            try:
                with open(filepath, "rb") as f:
                    response = openai.files.create(
                        file=(filename, f, mime_type),
                        purpose="assistants"
                    )
                file_id = response.id
                print(f"✅ Uploaded: {filename} → ID: {file_id}")
                
                # Cache the file_id by content hash for 30 days
                if content_hash:
                    cache.set(CacheTypes.VECTOR_STORE, content_hash, file_id, ttl_seconds=2592000)
                    print(f"📋 Cached file mapping for future deduplication")
                
                return file_id
            except Exception as e:
                print(f"⚠️ Upload failed (attempt {attempt + 1}): {e}")
                time.sleep(2)

        print(f"❌ Giving up on {filename} after {retries} attempts")
    except Exception as e:
        print(f"❌ Unexpected error uploading {filename}:")
        traceback.print_exc()
    return None

# Add uploaded file to vector store
def add_to_vector_store(file_id):
    try:
        print(f"➕ Adding to vector store: {file_id}")
        openai.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        print(f"✅ Added to vector store: {file_id}")
    except Exception as e:
        print(f"❌ Failed to add to vector store: {e}")
        traceback.print_exc()

# Main pipeline
def collect_and_process_files():
    all_files = []

    for folder in [PDF_DIR, TEXT_DIR]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                full_path = os.path.join(folder, filename)
                if os.path.isfile(full_path):
                    if folder == TEXT_DIR and filename.endswith(".txt"):
                        pdf_path = convert_txt_to_pdf(full_path)
                        if pdf_path:
                            all_files.append(pdf_path)
                    else:
                        all_files.append(full_path)

    for path in all_files:
        file_id = upload_file(path)
        if file_id:
            uploaded_file_ids.append(file_id)
            add_to_vector_store(file_id)

    # Save uploaded file IDs
    with open("uploaded_file_ids.txt", "w") as f:
        for fid in uploaded_file_ids:
            f.write(f"{fid}\n")

    print(f"\n🎉 Uploaded and added {len(uploaded_file_ids)} files to vector store '{vector_store_id}'.")


# Run the pipeline
if __name__ == "__main__":
    collect_and_process_files()
