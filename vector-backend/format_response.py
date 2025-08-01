import re
from urllib.parse import urlparse
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def filename_to_url(filename: str) -> str:
    """
    Convert filename to URL with better error handling
    Expected format: https___domain.com_path_to_page.pdf
    """
    try:
        original_filename = filename
        
        # Step 1: Replace only the first `___` with `://`
        if "___" in filename:
            filename = filename.replace("___", "://", 1)
        else:
            # If no protocol separator, assume https
            filename = "https://" + filename

        # Step 2: Replace underscores with slashes (but preserve domain)
        parts = filename.split("://")
        if len(parts) != 2:
            # Malformed URL, return a basic fallback
            return f"https://example.com/{original_filename}"
            
        protocol = parts[0]
        rest = parts[1]
        
        # Split domain from path
        domain_and_path = rest.split("_", 1)
        if len(domain_and_path) == 2:
            domain, path = domain_and_path
            # Replace underscores with slashes in path only
            path = path.replace("_", "/")
            url = f"{protocol}://{domain}/{path}"
        else:
            # No path, just domain
            url = f"{protocol}://{rest}"

        # Step 3: Remove .pdf and trailing underscores/slashes
        url = url.rstrip("_").rstrip("/").removesuffix(".pdf")
        
        # Validate the URL has a proper domain
        parsed = urlparse(url)
        if not parsed.netloc:
            return f"https://example.com/{original_filename}"
            
        return url
        
    except Exception as e:
        print(f"Error converting filename to URL: {filename} -> {e}")
        return f"https://example.com/{filename}"

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
                
                # Extract domain with fallback
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace("www.", "")
                
                # Handle empty domain (malformed URL)
                if not domain:
                    # Try to extract domain from filename
                    if "___" in filename:
                        domain_part = filename.split("___")[1].split("_")[0]
                        domain = domain_part.replace(".pdf", "")
                    else:
                        domain = "Unknown Source"
                
                # Final check for empty domain
                if not domain or domain.strip() == "":
                    domain = "Unknown Source"
                
                replacement_map[placeholder] = f"[{domain}]({url})"
                
            except Exception as e:
                print(f"Error processing citation {file_id}: {e}")
                # Safe fallback - try to get filename without URL conversion
                try:
                    file_info = client.files.retrieve(file_id)
                    filename = file_info.filename
                    # Extract basic domain from filename
                    if "___" in filename:
                        domain = filename.split("___")[1].split("_")[0].replace(".pdf", "")
                    else:
                        domain = "Document"
                    replacement_map[placeholder] = f"[{domain}](#{file_id})"
                except:
                    # Ultimate fallback
                    replacement_map[placeholder] = f"[Source](#{file_id})"

    for placeholder, replacement in replacement_map.items():
        text = text.replace(placeholder, replacement)

    return text
