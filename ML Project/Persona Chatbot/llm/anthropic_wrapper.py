import os

from langchain_anthropic import ChatAnthropic

from .llm_base import LLMBase
from utils.logger import Logger

class AnthropicWrapper(LLMBase):
    """Wrapper for Anthropic Solar model"""
    def __init__(self, model_name="claude-3-5-sonnet-20240620", temperature=0):
        self.llm = ChatAnthropic(
            model_name=model_name,
            temperature=temperature,
        )
        self.logger = Logger(os.getenv("LOG_LEVEL"))
        self.logger.debug(f"[AnthropicWrapper] Anthropic LLM instance [{model_name}] is initialised")

    def get_llm(self):
        """Return the Anthropic Solar LLM instance"""
        return self.llm
