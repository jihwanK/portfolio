import os

from langchain.docstore.document import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from utils.logger import Logger

class VectorStore:
    def __init__(self, script_path="./artefact/pooh_script.txt", index_path="./artefact/pooh_faiss"):
        self.script_path = script_path
        self.index_path = index_path
        self.embed_model = OpenAIEmbeddings(model="text-embedding-3-small")
        self.logger = Logger(os.getenv("LOG_LEVEL"))
        self.vector_store = None
        self.retriever = None

        self._generate_vector_store()
        self._generate_retriever()
        self.logger.debug("[VectorStore] Vector store is ready")

    def _load_script(self):
        with open(self.script_path, "r") as file:
            lines = "\n".join(file.readlines()).split("###\n")
        doc_script = [Document(page_content=script_parsed, metadata={"source": "Pooh"}) for script_parsed in lines]
        self.logger.debug("[VectorStore] Script is loaded")
        return doc_script

    def _generate_vector_store(self):
        if os.path.exists(self.index_path):
            self.vector_store = FAISS.load_local(self.index_path, embeddings=self.embed_model, allow_dangerous_deserialization=True)
            self.logger.debug(f"[VectorStore] Loaded existing vector store from {self.index_path}")
        else:
            doc_script = self._load_script()
            self.vector_store = FAISS.from_documents(doc_script, self.embed_model)
            self.vector_store.save_local(self.index_path)
            self.logger.debug(f"[VectorStore] Vector store generated and saved to {self.index_path}")

    def get_vector_store(self):
        self.logger.debug("[VectorStore] Get vector store")
        return self.vector_store

    def _generate_retriever(self):
        self.retriever = self.vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 3})
        self.logger.debug("[VectorStore] Retriever is generated")

    def get_retriever(self):
        self.logger.debug("[VectorStore] Get retriever")
        return self.retriever

