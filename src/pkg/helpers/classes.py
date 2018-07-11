import logging,sys,os,datetime, helpers.utils 
from helpers.config import *

class Video:

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
    
    @staticmethod
    def generate_output_path(videofile, src_root, dst_root, codec):
        fname = os.path.splitext(os.path.basename(videofile))[0]+codec.post + "." + codec.container
        targetdir = os.path.dirname(videofile)+os.path.sep
        if not dst_root:
            targetdir = targetdir + codec.name
        if dst_root:
            targetdir = targetdir.replace(src_root, dst_root)
        ret = os.path.join(targetdir,fname)
        return ret
    
    def __init__(self, file, src_root, dst_root, codec, forced):
        self.origFile = file
        self.targetFile = self.generate_output_path(file, src_root, dst_root, codec)
        self.codec = codec
        self.execCode = -99
        self.width = int(helpers.utils.get_video_width(self.origFile))
        self.startDateTime = 0
        self.forced = forced
        self.stopDateTime = 0
        if os.path.exists(self.targetFile):
            self.existing = True
        else:
            self.existing = False  
    
class Encoder:

    def __init__(self, logger, ffmpeg, extraopts, tempfile):
        self.logger = logger
        self.ffmpeg = ffmpeg
        self.extraopts = extraopts
        self.tempfile = tempfile

    def encode(self, video):
        self.logger.warning("Transcoding "+video.origFile+" - "+video.codec.name)
        print(helpers.utils.get_video_width(video.origFile))
        print(video.codec.maxscale)
        self.rescaleopts = ""
        if ( video.width > int(video.codec.maxscale) ) and not helpers.config.Configuration.forcewidth:
            self.logger.warning("Rescaling to " + video.codec.maxscale)
            self.rescaleopts =  helpers.config.Configuration.rescale_opts.replace("[WIDTH]",video.codec.maxscale)
        else:
            self.logger.warning("Keeping original resolution: {}".format(video.width))
        command = self.ffmpeg + " " + self.extraopts + " \"" + video.origFile + "\" " + video.codec.options + " " + self.rescaleopts + " " + " \""  + self.tempfile +"\""
        self.logger.error(command)
        ret = os.system(command)
        self.logger.warning("ret: "+str(ret))
        return ret

class CodecTemplate:
    
    def __init__(self, name, options, container, maxscale=4096):
        self.name = name
        self.options = options
        self.container = container
        self.post = "_"+name
        self.maxscale  = maxscale
