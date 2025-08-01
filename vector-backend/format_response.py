import re
from urllib.parse import urlparse
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def filename_to_url(filename: str) -> str:
    # Step 1: Replace only the first `___` with `://`
    if "___" in filename:
        filename = filename.replace("___", "://", 1)
    else:
        filename = "https://" + filename

    # Step 2: Replace underscores with slashes (but not in domain)
    parts = filename.split("://")
    domain_and_path = parts[1].split("_", 1)
    if len(domain_and_path) == 2:
        domain, path = domain_and_path
        url = f"{parts[0]}://{domain}/{path}"
    else:
        url = filename.replace("_", "/")

    # Step 3: Remove .pdf and trailing underscores
    url = url.rstrip("_").removesuffix(".pdf")
    return url

def replace_citation_placeholders(message):
    text = message.content[0].text.value
    annotations = getattr(message.content[0].text, "annotations", [])

    replacement_map = {}
    for annotation in annotations:
        if annotation.type == "file_citation":
            placeholder = annotation.text
            file_id = annotation.file_citation.file_id

            try:
                file_info = client.files.retrieve(file_id)
                filename = file_info.filename
                url = filename_to_url(filename)
                domain = urlparse(url).netloc.replace("www.", "")
                replacement_map[placeholder] = f"[{domain}]({url})"
            except Exception as e:
                print(e)
                replacement_map[placeholder] = file_info.filename

    for placeholder, replacement in replacement_map.items():
        text = text.replace(placeholder, replacement)

    return text
