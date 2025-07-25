import openai
import os
from dotenv import load_dotenv
import mimetypes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directories
PDF_DIR = "downloaded_pdfs"
TEXT_DIR = "site_texts"
TEMP_CONVERTED_DIR = "converted_pdfs"
os.makedirs(TEMP_CONVERTED_DIR, exist_ok=True)

# Load your vector store ID
with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()

uploaded_file_ids = []

def convert_txt_to_pdf(txt_path):
    pdf_filename = os.path.splitext(os.path.basename(txt_path))[0] + ".pdf"
    pdf_path = os.path.join(TEMP_CONVERTED_DIR, pdf_filename)

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        c = canvas.Canvas(pdf_path, pagesize=LETTER)
        width, height = LETTER
        y = height - 40  # start from top

        for line in lines:
            line = line.strip()
            if not line:
                continue
            c.drawString(40, y, line)
            y -= 15
            if y < 40:
                c.showPage()
                y = height - 40

        c.save()
        print(f"📝 Converted: {txt_path} → {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"❌ Failed to convert {txt_path} to PDF: {e}")
        return None

def upload_file(filepath):
    try:
        filename = os.path.basename(filepath)
        print(f"📤 Uploading: {filename}")

        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = "application/octet-stream"

        with open(filepath, "rb") as f:
            response = openai.files.create(
                file=(filename, f, mime_type),
                purpose="assistants"
            )

        file_id = response.id
        print(f"✅ Uploaded: {filename} → ID: {file_id}")
        return file_id
    except Exception as e:
        print(f"❌ Failed to upload {filepath}: {e}")
        return None

def add_to_vector_store(file_id):
    try:
        print(f"📎 Adding to vector store: {file_id}")
        result = openai.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        print(f"✅ Added to vector store: {file_id}")
    except Exception as e:
        print(f"❌ Failed to add to vector store: {e}")

# Collect and process all files
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

    # Upload and add to vector store
    for path in all_files:
        file_id = upload_file(path)
        if file_id:
            uploaded_file_ids.append(file_id)
            add_to_vector_store(file_id)

    # Save uploaded file IDs
    with open("uploaded_file_ids.txt", "w") as f:
        for fid in uploaded_file_ids:
            f.write(f"{fid}\n")

    print(f"\n🗃️ Uploaded and added {len(uploaded_file_ids)} files to vector store '{vector_store_id}'.")
