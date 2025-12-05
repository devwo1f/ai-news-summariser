from app.news_client import get_news

def test_news_fetching():
    print("Testing News Fetching Logic...")
    
    query = "FC Barcelona"
    print(f"Searching for: {query}")
    
    try:
        articles = get_news(query)
        
        if not articles:
            print("No articles found or there was an error.")
            return

        print(f"Found {len(articles)} articles:\n")
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article.title}")
            print(f"   Source: {article.source_name}")
            print(f"   URL: {article.url}")
            print("-" * 40)
            
        print("\n✅ Phase 2 Test Passed: Data Layer is working!")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_news_fetching()