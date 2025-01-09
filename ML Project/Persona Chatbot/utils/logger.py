import logging

class Logger:
    def __init__(self, log_level="info", log_file="chatbot.log"):
        self.logger = logging.getLogger("ChatbotLogger")

        if log_level.lower() == "debug":
            level = logging.DEBUG
        elif log_level.lower() == "info":
            level = logging.INFO
        elif log_level.lower() == "warning":
            level = logging.WARNING
        elif log_level.lower() == "error":
            level = logging.ERROR
        else:
            raise ValueError(f"Unsupported log level: {log_level}")

        if not self.logger.hasHandlers():
            self.logger.setLevel(level)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            if level in [logging.DEBUG, logging.WARNING, logging.ERROR]:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(level)
                console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
                console_handler.setFormatter(console_formatter)
                self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

