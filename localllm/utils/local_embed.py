# === utils/local_embed.py ===
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_local_embed_model():
    return HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
