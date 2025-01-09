import os
from dotenv import load_dotenv
load_dotenv(override=True)
import argparse

from utils.logger import Logger
from chatbot.chatbot import Chatbot

def main(llm_platform):
    logger = Logger(os.getenv("LOG_LEVEL"))
    logger.debug("[main] Start")

    chatbot = Chatbot(llm_platform=llm_platform)
    chatbot.run()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Extract and process scripts from documents."
    )
    parser.add_argument(
        "--llm", type=str, default="openai", help="Specify the LLM platform to use (e.g., OpenAI, Upstage, Anthropic, or Google)."
    )

    args = parser.parse_args()
    main(args.llm)
