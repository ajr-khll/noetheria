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
import json
from cache_config import cache, CacheTypes

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directories
PDF_DIR = "downloaded_pdfs"
TEXT_DIR = "site_texts"
TEMP_CONVERTED_DIR = "converted_pdfs"
PROCESSED_FILES_LOG = "processed_files.json"
os.makedirs(TEMP_CONVERTED_DIR, exist_ok=True)

# Load vector store ID
with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()

uploaded_file_ids = []

def load_processed_files():
    """Load list of files that have been successfully processed"""
    if os.path.exists(PROCESSED_FILES_LOG):
        try:
            with open(PROCESSED_FILES_LOG, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load processed files log: {e}")
    return {"processed_files": [], "file_hashes": {}}

def save_processed_files(processed_data):
    """Save list of successfully processed files"""
    try:
        with open(PROCESSED_FILES_LOG, "w") as f:
            json.dump(processed_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save processed files log: {e}")

def mark_file_processed(filepath, file_id):
    """Mark a file as successfully processed and uploaded"""
    processed_data = load_processed_files()
    
    abs_path = os.path.abspath(filepath)
    content_hash = get_file_content_hash(filepath)
    
    if abs_path not in processed_data["processed_files"]:
        processed_data["processed_files"].append(abs_path)
    
    if content_hash:
        processed_data["file_hashes"][content_hash] = {
            "file_id": file_id,
            "original_path": abs_path,
            "processed_time": time.time()
        }
    
    save_processed_files(processed_data)

def is_file_already_processed(filepath):
    """Check if file has already been processed"""
    processed_data = load_processed_files()
    abs_path = os.path.abspath(filepath)
    
    # Check by absolute path
    if abs_path in processed_data["processed_files"]:
        return True
    
    # Check by content hash
    content_hash = get_file_content_hash(filepath)
    if content_hash and content_hash in processed_data["file_hashes"]:
        return True
    
    return False

def delete_file_safely(filepath):
    """Safely delete a file after successful upload"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Deleted original file: {filepath}")
            return True
    except Exception as e:
        print(f"⚠️ Could not delete {filepath}: {e}")
    return False

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
        return True
    except Exception as e:
        print(f"❌ Failed to add to vector store: {e}")
        traceback.print_exc()
        return False

# Main pipeline
def collect_and_process_files(delete_after_upload=True):
    all_files = []
    processed_count = 0
    skipped_count = 0

    print(f"🔍 Scanning directories for files...")

    for folder in [PDF_DIR, TEXT_DIR]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                full_path = os.path.join(folder, filename)
                if os.path.isfile(full_path):
                    
                    # Check if file has already been processed
                    if is_file_already_processed(full_path):
                        print(f"⏭️ Skipping already processed file: {filename}")
                        skipped_count += 1
                        continue
                    
                    if folder == TEXT_DIR and filename.endswith(".txt"):
                        # Check if we already processed this TXT file
                        pdf_path = convert_txt_to_pdf(full_path)
                        if pdf_path:
                            all_files.append((pdf_path, full_path))  # Store both PDF and original TXT path
                    else:
                        all_files.append((full_path, full_path))  # Same file for both processing and deletion

    print(f"📁 Found {len(all_files)} new files to process (skipped {skipped_count} already processed)")

    for process_path, original_path in all_files:
        print(f"\n📂 Processing: {os.path.basename(process_path)}")
        
        file_id = upload_file(process_path)
        if file_id:
            # Try to add to vector store
            if add_to_vector_store(file_id):
                uploaded_file_ids.append(file_id)
                
                # Mark both the processed file and original file as completed
                mark_file_processed(process_path, file_id)
                if process_path != original_path:  # For TXT->PDF conversion
                    mark_file_processed(original_path, file_id)
                
                processed_count += 1
                
                # Delete original files after successful upload if requested
                if delete_after_upload:
                    # Delete the original file
                    delete_file_safely(original_path)
                    
                    # If we converted TXT to PDF, also delete the temporary PDF
                    if process_path != original_path and process_path.startswith(TEMP_CONVERTED_DIR):
                        delete_file_safely(process_path)
                
                print(f"✅ Successfully processed: {os.path.basename(original_path)}")
            else:
                print(f"❌ Failed to add to vector store: {os.path.basename(process_path)}")
        else:
            print(f"❌ Failed to upload: {os.path.basename(process_path)}")

    # Save uploaded file IDs
    if uploaded_file_ids:
        with open("uploaded_file_ids.txt", "w") as f:
            for fid in uploaded_file_ids:
                f.write(f"{fid}\n")

    print(f"\n🎉 Successfully processed {processed_count} files")
    print(f"📋 Skipped {skipped_count} already processed files")
    print(f"📊 Vector store '{vector_store_id}' now contains these newly added files.")


# Run the pipeline
if __name__ == "__main__":
    collect_and_process_files()
