from app.models import extract_content, summarize_article

def test_ai_pipeline():
    print("🧪 Testing AI & Scraping Pipeline...")
    
    # We use a list of URLs. If one fails (404 or blocked), we try the next.
    test_urls = [
        "https://www.bbc.com/news/world-us-canada-68963503", 
        "https://en.wikipedia.org/wiki/Artificial_intelligence", # Wikipedia is very scraper-friendly
        "https://www.reuters.com/technology/artificial-intelligence/"
    ]
    
    full_text = None
    used_url = ""

    for url in test_urls:
        print(f"\n1. Attempting to extract content from: {url}")
        full_text = extract_content(url)
        
        if full_text:
            used_url = url
            break # Stop loop if we got text
        else:
            print(f"   ⚠️ Failed. (The site might be blocking scrapers or the link is dead).")

    if full_text:
        print(f"✅ Extraction Successful! (Length: {len(full_text)} chars)")
        print(f"Snippet: {full_text[:200]}...\n")
        
        print("2. Generating Summary (Model is thinking...)...")
        summary = summarize_article(full_text)
        
        print("\n" + "="*40)
        print("🤖 AI SUMMARY:")
        print("="*40)
        print(summary)
        print("="*40)
        print("\n✅ Phase 3 Test Passed!")
    else:
        print("\n❌ Failed to extract content from ALL test URLs.")
        print("Check your internet connection or try adding a different URL to the list.")

if __name__ == "__main__":
    test_ai_pipeline()