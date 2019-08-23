import os,datetime,sys,json,tempfile,string,random
from helpers.classes import CodecTemplate
from os.path import expanduser


def sthing():
    print("smth")

class Configuration:
    progname = "massento"
    # logs the process here

    ffprobe_opts = "-v error -select_streams v:0 -show_format -show_streams  -of default=noprint_wrappers=1"
    ffprobe_width = "-v error -of flat=s=_ -select_streams v:0 -show_entries stream=width"
    logfilename = "log.txt"
    listfilename = "list.txt"
    temppath=tempfile.gettempdir()
    loglevel = "INFO"

    # finding out logfile location
    if os.name == "posix":
        logpath=expanduser("~") + os.path.sep + progname
        ffmpeg="ffmpeg"
        ffprobe="ffprobe"
    else:
        logpath=os.getenv('LOCALAPPDATA') + os.path.sep + progname
        ffmpeg="ffmpeg"
        ffprobe="ffprobe"
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logfile=logpath + os.path.sep + logfilename
    
    tempfile=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    task_list=logpath + os.path.sep + listfilename
    
    extensions=('avi','mpg','mpeg','mpv','mp4','mkv','mov')
    extraopts="-v info -y -i"
    rescale_opts="-vf scale=[WIDTH]:-2,format=yuv420p"
    
    log_date_format="%Y-%m-%d %H:%M:%S"
    statfile_name_date="%Y%m%d-%H-%M-%S"
    statfile=logpath + os.path.sep + "stats_" + datetime.datetime.now().strftime(statfile_name_date) + ".csv"
    
    codecs = []
    codecs.append(CodecTemplate("mp3","-c:v copy -c:a libmp3lame -q:a 5 -movflags +faststart","mp4"))
    codecs.append(CodecTemplate("x264","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a copy -movflags +faststart","mp4"))
    codecs.append(CodecTemplate("x264","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a copy -movflags +faststart","mp4"))
    codecs.append(CodecTemplate("x265","-c:v libx265 -preset slow -crf 20 -c:a copy -movflags +faststart","mp4"))
    codecs.append(CodecTemplate("x265_aac","-c:v libx265 -preset slow -crf 20 -c:a aac -ab 160k -movflags +faststart","mp4"))
    codecs.append(CodecTemplate("x264_aac","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a aac -ab 160k -movflags +faststart","mp4"))
    codecs = {codec.name:codec for codec in codecs}
    encode_identifiers = ["xvid","mplayer"]

    selected_codecs = {}
    files = []
    stats = []
    force_encode = False
    paranoid = False
    forcewidth = False
    dst_root = ""
    src_root = ""
    analyze = False
    logger = False
    copy_only = False
    delete_input = False
    service_mode = False
    
    def process_args(self,args):

        if args.temppath:
            self.temppath = args.temppath
            #self.logfile = self.temppath + os.path.sep + "log.txt"
            #self.task_list = self.temppath + os.path.sep + "list.txt"

        if args.encoder:
            self.ffmpeg = args.encoder
    
        if not args.templates:
            self.selected_codecs = self.codecs
        else:
            codec_names_argumentlist = args.templates.split(",")
            for codec_name in codec_names_argumentlist:
                if codec_name not in [codec.name for key,codec in self.codecs.items()]:
                    print("Unknown codec: " + str(codec_name))
                else:
                    self.selected_codecs[codec_name] = self.codecs[codec_name]
            if not self.selected_codecs:
                print("")
                print("There is no known codec given.")
                print("Known codecs: " + str(self.codecs.keys()))
                print("Exiting...")
                sys.exit(1)
        
        if args.show:
            print("Available templates")
            print("")
            for key,codec in self.codecs.items():
                print(codec.name+":    " + codec.options + ' ('+codec.container + ')')
            print()
            print("ffmpeg: " + self.ffmpeg)
            print("temppath: " + self.temppath)
            print("EXTENSION FILTER: " + str(self.extensions))
            sys.exit(1)
    
        if args.force:
            self.force_encode = True
    
        if args.paranoid:
            print("Paranoid Mode is enabled")
            self.paranoid = True
    
        if args.root:
            self.dst_root = (args.root + os.path.sep).replace(os.path.sep*2, os.path.sep)
    
        if args.analyze:
            self.analyze =  True
        
        if args.forcewidth:
            self.forcewidth = True
    
        if args.copy:
            if not args.root:
                print("With -c you must use -r!")
                print("Exiting...")
                sys.exit(1)
            self.copy_only = True

    def __init__(self,file):
        with open(file) as data:
            d = json.load(data)
            if 'templates' in d:
                templates = d["templates"]
                if len(templates) > 0:
                    self.codecs = {}
                    for templateid in templates.keys():
                        maxscale = 4096
                        if "maxscale" in templates[templateid]:
                            maxscale = templates[templateid]["maxscale"]
                            if(not maxscale.isdigit()):
                                maxscale = 4096
                        self.codecs[templateid] =  CodecTemplate(templateid,templates[templateid]["opts"],templates[templateid]["container"],maxscale)
            if 'ffmpeg' in d:
                self.ffmpeg = d["ffmpeg"]
            if 'temppath' in d:
                self.temppath = d["temppath"]
                self.logfile = self.temppath + os.path.sep + self.logfilename
                self.task_list = self.temppath + os.path.sep + self.listfilename
            if 'extensions_filter' in d:
                self.extensions = tuple(d["extensions_filter"])
            if 'encode_identifiers' in d:
                self.encode_identifiers = tuple(d["encode_identifiers"])
            if 'ffprobe' in d:
                self.ffprobe = str(d["ffprobe"])
            if 'ffprobe_opts' in d:
                self.ffprobe_opts = str(d["ffprobe_opts"])
            if 'ffprobe_width' in d:
                self.ffprobe_width = str(d["ffprobe_width"])
            if 'ffmpeg_scaleopt' in d:
                self.ffmpeg_scaleopt = str(d["ffmpeg_scaleopt"])