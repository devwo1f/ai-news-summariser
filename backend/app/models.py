from transformers import pipeline
import trafilatura

# Initialize the summarization model
# "facebook/bart-large-cnn" is excellent for news but can be heavy on CPU.
# If it's too slow, try "sshleifer/distilbart-cnn-12-6" which is faster.
print("Loading ML Model... (this might take a while usually once)")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_content(url: str) -> str | None:
    """
    Downloads the full article text from a given URL.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        print(f"Error extracting content: {e}")
        return None

def summarize_article(text: str) -> str:
    """
    Generates a summary of the provided text using the ML model.
    """
    if not text:
        return "No content to summarize."
    
    # News articles can be long. We truncate to 1024 chars for speed/memory 
    # if you want higher accuracy on long texts, you can increase this limit,
    # but the model has a hard limit around 1024 tokens.
    input_text = text[:3000] 

    try:
        # Generate summary
        # max_length: The max summary size
        # min_length: The minimum summary size
        summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing: {e}")
        return "Error generating summary."