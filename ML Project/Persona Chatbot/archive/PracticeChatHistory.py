from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnableLambda
import os
from logger import Logger

class chatbot:
    def __init__(self, retriever, llm, prompt):
        self.logger = Logger(os.getenv('LOG_LEVEL'))
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt
        self.memory = ConversationBufferWindowMemory(k=3,
                                                     ai_prefix=["Pooh", "Tigger", "Piglet", "Eeyore"])
    def merge_docs(self, retrieved_docs):
        return "###\n\n".join([d.page_content for d in retrieved_docs])

    def chain(self):
        holmes_chain_memory = RunnableParallel({
            "context": self.retriever | self.merge_docs,
            "query": RunnablePassthrough(),
            "history": RunnableLambda(self.memory.load_memory_variables) | itemgetter('history')
        })\
                              |  {
                                  "answer": self.prompt | self.llm | StrOutputParser(),
                                  "context": itemgetter("context"),
                                  "prompt": self.prompt}
        return holmes_chain_memory

    def chatbot(self, query):
        holmes_chain_memory = self.chain()
        result = holmes_chain_memory.invoke(query)
        self.memory.save_context({'query': query}, {"answer": result["answer"]})

        print(result["prompt"].messages[0].content.split("###")[-1] + result['answer'])
