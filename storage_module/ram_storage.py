# import storage_module.config_data as config_data
# import universal_module.utils
# import logging
# import sys


# logger = logging.getLogger("Main")
# sys.excepthook = universal_module.utils.log_exception_handler


class RAMStorage:
    def __init__(self):
        self.total_messages_read: int = 0
        self.total_messages_sent: int = 0
