import logging


class Logger:
    def __init__(self, name, log_file="game.log"):
        self.log = logging.getLogger(name=name)
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="{asctime}: {name}: {levelname}: {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )
        file_handler = logging.FileHandler(filename=log_file, mode="w")
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        self.log.addHandler(console_handler)
        self.log.addHandler(file_handler)

    def get_logger(self):
        return self.log
