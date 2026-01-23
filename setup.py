"""
Setup script to download required NLTK data for the Mental Health Chatbot
"""
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    
    try:
        nltk.download('punkt', quiet=True)
        print("✓ Downloaded punkt")
        
        nltk.download('brown', quiet=True)
        print("✓ Downloaded brown")
        
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✓ Downloaded averaged_perceptron_tagger")
        
        print("\n✅ All NLTK data downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

if __name__ == "__main__":
    download_nltk_data()
