# === utils/local_llm.py ===
from llama_index.core import ServiceContext
from llama_index.llms.llama_cpp import LlamaCPP
from utils.local_embed import get_local_embed_model

def get_local_llm(embed_model=False):
    llm = LlamaCPP(
        model_path="models/tinyllama-1.1B-chat.Q4_K_M.gguf",
        temperature=0.7,
        context_window=2048,
        max_new_tokens=256,
    )

    return ServiceContext.from_defaults(
        llm=llm,
        embed_model=get_local_embed_model() if embed_model else None,
    )
