import os

from langchain_google_genai import ChatGoogleGenerativeAI

from .llm_base import LLMBase
from utils.logger import Logger

class GeminiWrapper(LLMBase):
    """Wrapper for Google's Gemini model"""
    def __init__(self, model_name="gemini-1.5-pro", temperature=0):
        self.llm = ChatGoogleGenerativeAI(
            model_name=model_name,
            temperature=temperature,
        )
        self.logger = Logger(os.getenv("LOG_LEVEL"))
        self.logger.debug(f"[GeminiWrapper] Gemini LLM instance [{model_name}] is initialised")

    def get_llm(self):
        """Return the Google Gemini LLM instance"""
        return self.llm
