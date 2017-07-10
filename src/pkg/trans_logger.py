import logging,sys

class MyLogger:
    
    def __init__(self, logfile, log_date_format):
        self.logfile = logfile
        self.logFormatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s',datefmt=log_date_format)
  
        rootLogger = logging.getLogger()
    
        fileHandler = logging.FileHandler(self.logfile)
        fileHandler.setFormatter(self.logFormatter)
        fileHandler.setLevel(logging.INFO)
        rootLogger.addHandler(fileHandler)
    
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(self.logFormatter)
        consoleHandler.setLevel(logging.WARNING)
        rootLogger.addHandler(consoleHandler)
        rootLogger.setLevel(logging.INFO)
        self.rootLogger = rootLogger

    def getLogger(self):
        return self.rootLogger
