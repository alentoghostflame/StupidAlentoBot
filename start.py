from main_bot import StupidAlentoBot
from universal_module import utils
# from datetime import datetime
import logging
import sys
import os


FORMAT = "[{asctime}][{filename}][{lineno:3}][{funcName}][{levelname}] {message}"
LOGGING_LEVEL = logging.DEBUG


def setup_logging():
    setup_logger = logging.getLogger("Main")
    log_format = logging.Formatter(FORMAT, style="{")

    os.makedirs("logs", exist_ok=True)
    # time_string = datetime.now().isoformat()
    # log_file_handler = logging.FileHandler("logs/SAB {}.log".format(time_string), mode="w+")
    log_latest_handler = logging.FileHandler("logs/SAB Latest.log", mode="w+")

    # log_file_handler.setFormatter(log_format)
    log_latest_handler.setFormatter(log_format)
    log_console_handler = logging.StreamHandler(sys.stdout)
    log_console_handler.setFormatter(log_format)

    # setup_logger.addHandler(log_file_handler)
    setup_logger.addHandler(log_latest_handler)
    setup_logger.addHandler(log_console_handler)

    setup_logger.setLevel(LOGGING_LEVEL)
    sys.excepthook = utils.log_exception_handler


stupid_bot = StupidAlentoBot()
logger = logging.getLogger("Main")
try:
    setup_logging()
    # logger = logging.getLogger("Main")
    # stupid_bot = StupidAlentoBot()
    stupid_bot.load_data()
    # stupid_bot.update_data()
    stupid_bot.run()
    stupid_bot.save_data()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED:")
    logger.exception(e)
    stupid_bot.save_data()
# setup_logging()
# # logger = logging.getLogger("Main")
# # stupid_bot = StupidAlentoBot()
# stupid_bot.load_data()
# # stupid_bot.update_data()
# stupid_bot.run()
# stupid_bot.save_data()
