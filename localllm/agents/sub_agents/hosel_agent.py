import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from utils.local_llm import get_local_llm
from localllm.agents.utils.local_embed import get_local_embed_model


class HostelAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="HostelAgent", description="Handles hostel-related queries.")
        self.query_engine = self._setup_query_engine()

    def _setup_query_engine(self):
        storage_dir = os.path.join("query_engine_storage", "hostel")
        if os.path.exists(storage_dir):
            print("✅ Loading existing vector index for hostel agent...")
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            index = load_index_from_storage(storage_context)
        else:
            print("📁 Creating new vector index for hostel agent...")
            documents = SimpleDirectoryReader("data/hostel").load_data()
            index = VectorStoreIndex.from_documents(
                documents,
                service_context=get_local_llm(embed_model=True),
            )
            index.storage_context.persist(persist_dir=storage_dir)

        return index.as_query_engine()

    async def run(self, message: str) -> str:
        response = self.query_engine.query(message)
        return str(response)
