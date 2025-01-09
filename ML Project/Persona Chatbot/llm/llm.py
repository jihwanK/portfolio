from .openai_wrapper import OpenAIWrapper
from .upstage_wrapper import UpstageWrapper
from .gemini_wrapper import GeminiWrapper
from .anthropic_wrapper import AnthropicWrapper

class LLM:
    """Factory to create instances of different language models."""

    @staticmethod
    def create_llm(platform, **kwargs):
        if platform.lower() == "openai" or platform.lower() == "chatgpt" or platform.lower() == "gpt":
            return OpenAIWrapper(**kwargs).get_llm()
        elif platform.lower() == "upstage" or platform.lower() == "solar":
            return UpstageWrapper(**kwargs).get_llm()
        elif platform.lower() == "gemini" or platform.lower() == "google":
            return GeminiWrapper(**kwargs).get_llm()
        elif platform.lower() == "claude" or platform.lower() == "anthropic":
            return AnthropicWrapper(**kwargs).get_llm()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
