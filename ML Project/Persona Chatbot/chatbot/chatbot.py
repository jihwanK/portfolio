import os
import re

from operator import itemgetter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory

from utils.logger import Logger
from llm.llm import LLM
from vector_store.vector_store import VectorStore
from . import prompt

class Chatbot():
    def __init__(self, llm_platform="openai"):
        self.logger = Logger(os.getenv("LOG_LEVEL"))

        self.vector_store = VectorStore()
        self.llm = LLM().create_llm(llm_platform)
        self.retriever = self.vector_store.get_retriever()
        self.prompt = prompt.get_prompt()
        self.memory = ConversationBufferWindowMemory(
            k=25,
            ai_prefix="Pooh and his friends",
            human_prefix="User"
        )
        self.logger.debug("[Chatbot] Chatbot system is initialised")

    def _merge_docs(self, retrieved_docs):
        self.logger.debug(f"[Chatbot] Merge documents: Retrieved docs: {retrieved_docs}")
        return "###\n\n".join([d.page_content for d in retrieved_docs])

    def _chain(self):
        self.logger.debug("[Chatbot] Create chain")
        chain_memory = RunnableParallel({
            "context": itemgetter("query") | self.retriever | self._merge_docs,
            "query": itemgetter("query") | RunnablePassthrough(),
            "history": RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
            "name": itemgetter("name") | RunnablePassthrough(),
        }) | {
            "prompt": self.prompt,
            "answer": self.prompt | self.llm | StrOutputParser(),
        }
        return chain_memory

    def _chat(self, query, user_name):
        self.logger.debug("[Chatbot] Start chat")
        chain_memory = self._chain()
        self.logger.debug("[Chatbot] Successfully generated chain")
        self.logger.debug(f"[Chatbot] chain generated === \n{chain_memory}")
        result = chain_memory.invoke({"query": query, "name": user_name})
        self.logger.debug(f"[Chatbot] chain invoked === \n{result}")
        self.logger.debug("[Chatbot] Successfully invoked chat")
        self.memory.save_context({"query": query}, {"answer": result["answer"].strip()})
        self.logger.debug(f"[Chatbot] Prompt token size: {len("\n".join([message.content for message in result["prompt"].messages]).split(" "))}")
        self.logger.debug("[Chatbot] Saved the chat history")

        self.logger.debug("\n".join(map(str.strip, re.sub(r"\n+", "\n", result["answer"]).split("\n"))))
        print("\n".join(map(str.strip, re.sub(r"\n+", "\n", result["answer"]).split("\n"))))
        return "\n\n".join(map(str.strip, re.sub(r"\n+", "\n", result["answer"]).split("\n")))

    def run_front(self, query, user_name):
        return self._chat(query, user_name)
    
    def run(self):
        self.logger.debug("[Chatbot] Chatbot system is running")

        user_name = input("Could you tell us your name please?\n")

        num_conversation = 1
        while True:
            query = input(f"\n({num_conversation})\n{user_name}: ")
            num_conversation += 1

            if query.lower() in ["exit", "finish", "quit"]:
                print("Thank you for chatting. Goodbye!")
                break

            self._chat(query, user_name)
