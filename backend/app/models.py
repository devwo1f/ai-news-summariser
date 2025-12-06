from transformers import pipeline
import trafilatura

# --- CONFIGURATION ---
# Switching to T5-Small for MAXIMUM SPEED.
# This model is tiny (~60MB) and very fast on CPU.
MODEL_NAME = "t5-small"

print(f"Loading Ultra-Fast ML Model ({MODEL_NAME})...")
try:
    # T5 requires the task to be specified in the pipeline definition for some versions,
    # but strictly speaking, it's a text2text-generation model. 
    # The 'summarization' pipeline handles the T5 prefixing automatically in newer versions,
    # but we will add it manually to be safe.
    summarizer = pipeline("summarization", model=MODEL_NAME)
except Exception as e:
    print(f"Error loading model: {e}")
    raise e

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
    
    # T5 is trained with a specific prefix "summarize: "
    input_text = "summarize: " + text[:2000] 

    try:
        # Generate summary
        summary = summarizer(input_text, max_length=100, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing: {e}")
        return "Error generating summary."