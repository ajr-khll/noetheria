import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Folders to clean
FOLDERS_TO_CLEAN = ["downloaded_pdfs", "converted_pdfs", "site_texts"]

def clean_up():
    with open("vector_store_id.txt", "r") as f:
        vector_store_id = f.read().strip()

    # Remove all files from vector store
    files = openai.vector_stores.files.list(vector_store_id=vector_store_id)
    for file in files.data:
        file_id = file.id
        print(f"Removing from vector store: {file_id}")
        openai.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)

    # Delete all uploaded files from OpenAI
    all_files = openai.files.list()
    for file in all_files.data:
        print(f"Deleting file: {file.id} ({file.filename})")
        openai.files.delete(file.id)

    # Empty the local folders
    for folder in FOLDERS_TO_CLEAN:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        print(f"🧹 Deleted local file: {file_path}")
                    except Exception as e:
                        print(f"❌ Failed to delete {file_path}: {e}")

    print("✅ Cleanup completed successfully.")

if __name__ == "__main__":
    clean_up()