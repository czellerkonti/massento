import logging,sys

class Video:

    def __init__(self, origpath, targetpath, codec):
        if not os.path.exists(origpath):
            self.existing = False
        else:
            self.sourcePath = origpath
            self.targetPath = targetpath
            self.codec = codec
        self.execCode = -99
        self.startDateTime = 0;
        self.stopDateTime = 0;

    def setStartTime(self):
        self.startDateTime = datetime.datetime.now()

    def setStopTime(self):
        self.stopDateTime = datetime.datetime.now()

    def setExecCode(self,execCode):
        self.execCode = execCode

    def getStartTime(self):
        if self.startDateTime == 0:
            return datetime.datetime.now()
        return self.startDateTime

    def getStopTime(self):
        if self.stopDateTime == 0:
            return datetime.datetime.now()
        return self.stopDateTime

class Encoder:

    def __init__(self, codecs, logger, ffmpeg):
        self.codecs = codecs
        self.logger = logger
        self.ffmpeg = ffmpeg

    def encode(self, codec, inputvideo, outvideo, extraopts):
        if codec not in self.codecs.keys():
            self.logger.error("Unknown codec: "+codec)
            return -1
        encode_options = self.codecs.get(codec)
        self.logger.warning("Transcoding "+inputvideo+" - "+codec)
        command = self.ffmpeg + " " + extraopts + " \"" + inputvideo + "\" " + encode_options + " " + outvideo
        self.logger.error(command)
        ret = os.system(command)
        self.logger.warning("ret: "+str(ret))
        return ret

class ConfigLogger:
    
    def __init__(self, logfile, log_date_format):
        self.logfile = logfile
        self.logFormatter = logging.Formatter('%(asctime)s %(message)s',datefmt=log_date_format)
        rootLogger = logging.getLogger()
    
        fileHandler = logging.FileHandler(self.logfile)
        fileHandler.setFormatter(self.logFormatter)
        fileHandler.setLevel(logging.INFO)
        rootLogger.addHandler(fileHandler)
    
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(self.logFormatter)
        consoleHandler.setLevel(logging.WARNING)
        rootLogger.addHandler(consoleHandler)
        rootLogger.setLevel(logging.WARNING)
        self.rootLogger = rootLogger

    def getLogger(self):
        return self.rootLogger

class CodecTemplate:
    
    def __init__(self, name, options, container):
        self.name = name
        self.options = options
        self.container = container