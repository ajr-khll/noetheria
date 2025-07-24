import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def clean_up():
    with open("vector_store_id.txt", "r") as f:
        vector_store_id = f.read().strip()
    f.close()

    # List all files in the vector store
    files = openai.vector_stores.files.list(vector_store_id=vector_store_id)

    for file in files.data:
        file_id = file.id
        print(f"Removing from vector store: {file_id}")
        openai.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)


    # List all files in your account
    all_files = openai.files.list()

    for file in all_files.data:
        print(f"Deleting file: {file.id} ({file.filename})")
        openai.files.delete(file.id)

if __name__ == "__main__":
    clean_up()
    print("Cleanup completed successfully.")