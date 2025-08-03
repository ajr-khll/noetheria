# embedding.py
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("[MODEL] Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[MODEL] Model loaded and cached")
    return _model

def embed_text(text):
    model = get_model()
    return model.encode(text[:3000])  # truncate to fit input size
