from datetime import datetime
from main_bot import StupidAlentoBot
import stupid_utils
# import traceback
import logging
import sys
import os


FORMAT = "[{asctime}][{filename}][{lineno:3}][{funcName}][{levelname}] {message}"
LOGGING_LEVEL = logging.DEBUG


# def log_exception_handler(error_type, value, tb):
#     # TODO: Unify logging errors.
#     the_logger = logging.getLogger("Main")
#     the_logger.critical("Uncaught exception:\n"
#                         "Type: {}\n"
#                         "Value: {}\n"
#                         "Traceback:\n {}".format(str(error_type), str(value), "".join(traceback.format_tb(tb))))


def setup_logging():
    setup_logger = logging.getLogger("Main")
    log_format = logging.Formatter(FORMAT, style="{")

    os.makedirs("logs", exist_ok=True)
    time_string = datetime.now().isoformat()
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
    sys.excepthook = stupid_utils.log_exception_handler


stupid_bot = StupidAlentoBot()
logger = logging.getLogger("Main")
try:
    setup_logging()
    # logger = logging.getLogger("Main")
    # stupid_bot = StupidAlentoBot()
    stupid_bot.load_data()
    stupid_bot.update_data()
    stupid_bot.run()
    stupid_bot.save_data()
except:
    logger.critical("SOMETHING TERRIBLE HAPPENED!")
    stupid_bot.save_data()