import sys
import traceback
from logger.custom_logger import CustomLogger

log = CustomLogger().get_logger(__file__)

class CustomException:
    """A class for raising custom exception"""
    
    def __init__(self, error_message, error_details:sys):
        
        _,_,exc_tb = error_details.exc_info()
        ## capture filename
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        ## capture lineno
        self.line_no = exc_tb.tb_lineno
        self.error_message = str(error_message)
        ## capture complete traceback
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
        
    def __str__(self):
        return f"""
        Error in [{self.file_name}] at line no [{self.line_no}]
        Message : {self.error_message}
        Traceback:
        {self.traceback_str}
        """
        
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc=CustomException(e,sys)
        log.error(app_exc)
        raise app_exc       