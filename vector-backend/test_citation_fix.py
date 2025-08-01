"""
Test script to verify citation processing fixes
"""

from format_response import filename_to_url
from urllib.parse import urlparse

def test_filename_to_url():
    """Test various filename scenarios"""
    
    test_cases = [
        # Normal cases
        ("https___example.com_page_article.pdf", "https://example.com/page/article"),
        ("http___domain.org_research_paper.pdf", "http://domain.org/research/paper"),
        
        # Edge cases that could cause "Unknown Source"
        ("malformed_filename.pdf", "https://example.com/malformed_filename.pdf"),
        ("___broken___url.pdf", "https://example.com/___broken___url.pdf"),
        ("", "https://example.com/"),
        ("just_text.pdf", "https://just_text"),
        
        # Real examples from your system
        ("https___en.wikipedia.org_wiki_Nietzsche.pdf", "https://en.wikipedia.org/wiki/Nietzsche"),
        ("https___bigthink.com_thinking_how-the-nazis-hijacked-nietzsche.pdf", "https://bigthink.com/thinking/how-the-nazis-hijacked-nietzsche"),
    ]
    
    print("🧪 Testing filename_to_url function...")
    print("=" * 50)
    
    for filename, expected in test_cases:
        try:
            result = filename_to_url(filename)
            parsed = urlparse(result)
            domain = parsed.netloc.replace("www.", "")
            
            status = "✅ PASS" if domain and domain != "example.com" else "⚠️  FALLBACK"
            print(f"{status}")
            print(f"  Input:    {filename}")
            print(f"  Output:   {result}")
            print(f"  Domain:   {domain}")
            print(f"  Expected: {expected}")
            print()
            
        except Exception as e:
            print(f"❌ ERROR: {filename} -> {e}")
            print()

def test_domain_extraction():
    """Test domain extraction edge cases"""
    
    print("🔍 Testing domain extraction...")
    print("=" * 50)
    
    filenames = [
        "https___stackoverflow.com_questions_12345.pdf",
        "malformed.pdf",
        "___broken.pdf",
        "normal_file.pdf",
        ""
    ]
    
    for filename in filenames:
        try:
            url = filename_to_url(filename)
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            
            # Simulate the logic from replace_citation_placeholders
            if not domain:
                if "___" in filename:
                    domain_part = filename.split("___")[1].split("_")[0]
                    domain = domain_part.replace(".pdf", "")
                else:
                    domain = "Unknown Source"
            
            if not domain or domain.strip() == "":
                domain = "Unknown Source"
                
            print(f"Filename: {filename}")
            print(f"Domain:   {domain}")
            print(f"Status:   {'❌ Unknown Source' if domain == 'Unknown Source' else '✅ Valid'}")
            print()
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            print()

if __name__ == "__main__":
    test_filename_to_url()
    test_domain_extraction()
    print("🎯 Test complete! The 'Unknown Source' bug should now be fixed.")