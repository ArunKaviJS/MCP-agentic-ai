import os
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.query_engine import RetrieverQueryEngine

def query_document(query: str, system_prompt: str, top_k: int = 3) -> str:
    try:
        storage_path = "query-engine-storage"
        storage_context = StorageContext.from_defaults(persist_dir=storage_path)

        index = load_index_from_storage(storage_context)
        retriever = index.as_retriever(similarity_top_k=top_k)

        llm = AzureOpenAI(
            deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"),
            model=os.getenv("AZURE_EMBED_MODEL"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            llm=llm,
            system_prompt=system_prompt,
        )

        response = query_engine.query(query)
        print(f"[VectorSearch] ➜ Query: '{query}' → Response: '{response}'")
        return str(response)

    except Exception as e:
        print(f"❌ Error in query_document: {e}")
        return "Sorry, I couldn't find an answer right now. Please try again later."
