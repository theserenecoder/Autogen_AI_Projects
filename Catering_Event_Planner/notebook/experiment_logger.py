import logging
import os
from datetime import datetime
import structlog
from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

class CustomLogger:
    """A class to log execution events"""
    
    def __init__(self, log_dir = 'logs'):
        ## insure log directory exists
        self.log_dir = os.path.join(os.getcwd(),log_dir)
        ## creating the directory, if exists will use that
        os.makedirs(self.log_dir, exist_ok=True)
        
        ## creating timestamp log filename
        log_file = f"{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log"
        self.log_file_path = os.path.join(self.log_dir,log_file)
        
        self._configure_autogen_loggers()
        
    def _configure_autogen_loggers(self):
        """Sets the logging levels for the AutoGen loggers."""
        # Get the AutoGen event logger and set its level.
        # This logger captures structured messages between agents.
        event_logger = logging.getLogger(EVENT_LOGGER_NAME)
        event_logger.setLevel(logging.INFO)

        # Get the AutoGen trace logger and set its level.
        # This logger captures detailed runtime events for debugging.
        trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
        trace_logger.setLevel(logging.DEBUG)
    
    
    def get_logger(self, name=__file__):
        
        logger_name = os.path.basename(name)
        
        ## configure logging for file (JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[file_handler]
        )
        
        ## Configuring for structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt='iso',utc=True, key='timestamp'),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to='event'),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True
        )
        return structlog.get_logger(logger_name)
    
if __name__ == '__main__':
    logger = CustomLogger().get_logger(__file__)
    logger.info("Testing log", user_id=123)