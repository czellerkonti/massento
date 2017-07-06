import logging,sys,os

class Videoo:

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
    
    def generate_output_path(videofile, src_root, dst_root,codec):
        fname = os.path.splitext(os.path.basename(videofile))[0]+codec.post + "." + codec.container
        targetdir=os.path.dirname(videofile)+os.path.sep
        if not dst_root:
            targetdir = targetdir + codec
        if dst_root:
            targetdir = targetdir.replace(src_root, dst_root)
        ret = os.path.join(targetdir,fname)
        return ret
    
    def __init__(self, file, src_root, dst_root, codec):
        if not os.path.exists(file):
            self.existing = False
        else:
            self.origFile = file
            self.targetFile = generate_output_path(file, src_root, dst_root, codec)
            self.codec = codec
        self.execCode = -99
        self.startDateTime = 0;
        self.stopDateTime = 0;

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

class CodecTemplate:
    
    def __init__(self, name, options, container):
        self.name = name
        self.options = options
        self.container = container
        self.post = "_"+name