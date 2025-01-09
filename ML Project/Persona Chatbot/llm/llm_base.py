from abc import ABC, abstractmethod

class LLMBase(ABC):
    """Abstract base class for different language model wrappers."""

    @abstractmethod
    def get_llm(self):
        """Return the initialized LLM instance."""
        pass
