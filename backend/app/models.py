from transformers import pipeline
import torch
import trafilatura

# --- CONFIGURATION ---
# 1. Summarization Model
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"

# 2. Sentiment Analysis Model (Fast & Light)
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# 3. Topic Classification Model (Zero-Shot)
# We use this to auto-tag articles (e.g. "Politics", "Sports")
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"

print("Loading AI Models... (This uses ~4GB VRAM)")

# Check for GPU
if torch.cuda.is_available():
    device = 0
    gpu_name = torch.cuda.get_device_name(0)
    print(f"   ✅ SUCCESS: Running on GPU: {gpu_name}")
else:
    device = -1
    print("   ⚠️ WARNING: Running on CPU. GPU not detected.")

try:
    # Load Pipelines
    print(f"   ...Loading Summarizer ({SUMMARIZATION_MODEL})")
    summarizer = pipeline("summarization", model=SUMMARIZATION_MODEL, device=device)
    
    print(f"   ...Loading Sentiment Analyzer ({SENTIMENT_MODEL})")
    sentiment_analyzer = pipeline("sentiment-analysis", model=SENTIMENT_MODEL, device=device)
    
    print(f"   ...Loading Topic Classifier ({CLASSIFICATION_MODEL})")
    classifier = pipeline("zero-shot-classification", model=CLASSIFICATION_MODEL, device=device)

    # --- PROOF OF GPU USAGE ---
    if device == 0:
        vram = torch.cuda.memory_allocated(0) / 1024**2
        print(f"   📊 Total VRAM Used: {vram:.2f} MB")

except Exception as e:
    print(f"Error loading models: {e}")
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
    Generates a summary using the BART model.
    """
    if not text: return "No content."
    input_text = text[:3000] 
    try:
        summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing: {e}")
        return "Error generating summary."

def analyze_sentiment(text: str) -> dict:
    """
    Returns {'label': 'POSITIVE'|'NEGATIVE', 'score': float}
    """
    if not text: return {"label": "NEUTRAL", "score": 0.0}
    
    # Sentiment models expect shorter text, so we use the first 512 chars
    input_text = text[:512]
    try:
        result = sentiment_analyzer(input_text)[0]
        return result
    except Exception as e:
        print(f"Error in sentiment: {e}")
        return {"label": "NEUTRAL", "score": 0.0}

def classify_category(text: str) -> str:
    """
    Categorizes the article into one of the predefined topics.
    """
    if not text: return "General"
    
    # We define the potential tags here
    candidate_labels = ["Politics", "Sports", "Business", "Technology", "Entertainment", "Health", "Science", "World News", "Finance"]
    
    # Use the first 1000 chars for classification to be fast
    input_text = text[:1000]
    
    try:
        result = classifier(input_text, candidate_labels)
        # result['labels'][0] is the highest confidence score label
        return result['labels'][0]
    except Exception as e:
        print(f"Error classifying: {e}")
        return "General"