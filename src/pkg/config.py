import os,datetime,sys

class Configuration:
    
    # logs the process here
    FFMPEG="d:\\Tools\\ffmpeg-3.2.4-win64-shared\\bin\\ffmpeg.exe"
    FFPROBE="d:\\Tools\\ffmpeg-3.2.4-win64-shared\\bin\\ffprobe.exe"
    FFPROBE_OPTS = "-v error -select_streams v:0 -show_format -show_streams  -of default=noprint_wrappers=1"
    #FFMPEG="ffmpeg"
    #TEMPPATH="/mnt/data/tmp"
    TEMPPATH="C:\\tmp\\"
    LOGFILE=TEMPPATH + os.path.sep + "actual.txt"
    
    TEMPFILE="temp"
    TASK_LIST=TEMPPATH + os.path.sep + "list.txt"
    
    
    EXTENSIONS=('avi','mpg','mpeg','mpv','mp4','mkv','mov')
    EXTRAOPTS="-v info -y -i"
    
    LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"
    STATFILE_NAME_DATE="%Y%m%d-%H-%M-%S"
    STATFILE=TEMPPATH + os.path.sep + "stats_" + datetime.datetime.now().strftime(STATFILE_NAME_DATE) + ".csv"
    
    CODECS = {}
    CODECS["mp3"]="-c:v copy -c:a libmp3lame -q:a 5 -movflags +faststart"
    CODECS["x264"]="-c:v libx264 -preset veryslow -crf 20 -tune film -c:a copy -movflags +faststart"
    CODECS["x265"]="-c:v libx265 -preset slow -crf 20 -c:a copy -movflags +faststart"
    CODECS["x265_aac"]="-c:v libx265 -preset slow -crf 20 -c:a aac -ab 160k -movflags +faststart"
    CODECS["x264_aac"]="-c:v libx264 -preset veryslow -crf 20 -tune film -c:a aac -ab 160k -movflags +faststart"
    
    CONTAINERS = {}
    CONTAINERS["mp3"]="mp4"
    CONTAINERS["x264"]="mp4"
    CONTAINERS["x265"]="mp4"
    CONTAINERS["x265_aac"]="mp4"
    CONTAINERS["x264_aac"]="mp4"
    
    POSTS = list("_" + post for post in CODECS.keys())
    POSTS.append("_enc")
    FAILED_VIDEOS = []
    SELECTED_CODECS = []
    FILES = []
    STATS = []
    FORCE_ENCODE = False
    PARANOID = False
    DST_ROOT = ""
    SRC_ROOT = ""
    ANALYZE = False
    ENCODE_IDENTIFIERS = ["xvid","mplayer"]
    COPY_ONLY = False
    LOGGER = None
    
    def __init__(self,args):
        if args.temppath:
            self.TEMPPATH = args.temppath
            self.LOGFILE = self.TEMPPATH + os.path.sep + "actual.txt"
            self.TASK_LIST = self.TEMPPATH + os.path.sep + "list.txt"
    
        if args.encoder:
            self.FFMPEG = args.encoder
    
        if not args.templates:
            self.SELECTED_CODECS = self.CODECS.keys()
        else:
            self.SELECTED_CODECS = args.templates.split(",")
            WRONG_CODECS = []
            for codec in self.SELECTED_CODECS:
                if codec not in self.CODECS.keys():
                    print("Unknown codec: " + str(codec))
                    WRONG_CODECS.append(codec)
            for c in WRONG_CODECS:
                self.SELECTED_CODECS.remove(c)
            if not self.SELECTED_CODECS:
                print("")
                print("There is no known codec given.")
                print("Known codecs: " + str(self.CODECS.keys()))
                print("Exiting...")
                sys.exit(1)
    
        if args.show:
            print("Available templates")
            print("")
            for key in self.CODECS.keys():
                print(key+":    " + self.CODECS.get(key) + ' ('+self.CONTAINERS.get(key) + ')')
            print()
            print("FFMPEG: " + self.FFMPEG)
            print("TEMPPATH: " + self.TEMPPATH)
            print("EXTENSION FILTER: " + str(self.EXTENSIONS))
            print("POSTS: " + str(self.POSTS))
            sys.exit(1)
    
        if args.force:
            self.FORCE_ENCODE = True
    
        if args.paranoid:
            self.PARANOID = True
    
        if args.root:
            self.DST_ROOT = (args.root + os.path.sep).replace(os.path.sep*2, os.path.sep)
    
        if args.analyze:
            self.ANALYZE =  True
    
        if args.copy:
            if not args.root:
                print("With -c you must use -r!")
                print("Exiting...")
                sys.exit(1)
            self.COPY_ONLY = True