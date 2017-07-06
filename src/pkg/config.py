import os,datetime,sys,json
from classes import CodecTemplate

class Configuration:
    
    # logs the process here
    ffmpeg="ffmpeg.exe"
    ffprobe="d:\\Tools\\ffmpeg-3.2.4-win64-shared\\bin\\ffprobe.exe"
    ffprobe_opts = "-v error -select_streams v:0 -show_format -show_streams  -of default=noprint_wrappers=1"
    #ffmpeg="ffmpeg"
    #temppath="/mnt/data/tmp"
    temppath="C:\\tmp\\"
    logfile=temppath + os.path.sep + "actual.txt"
    
    tempfile="temp"
    task_list=temppath + os.path.sep + "list.txt"
    
    extensions=('avi','mpg','mpeg','mpv','mp4','mkv','mov')
    extraopts="-v info -y -i"
    
    log_date_format="%Y-%m-%d %H:%M:%S"
    statfile_name_date="%Y%m%d-%H-%M-%S"
    statfile=temppath + os.path.sep + "stats_" + datetime.datetime.now().strftime(statfile_name_date) + ".csv"
    
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
    dst_root = ""
    src_root = ""
    analyze = False
    logger = False
    copy_only = False
    
    
    def process_args(self,args):

        if args.temppath:
            self.temppath = args.temppath
            self.logfile = self.temppath + os.path.sep + "actual.txt"
            self.task_list = self.temppath + os.path.sep + "list.txt"
    
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
            self.paranoid = True
    
        if args.root:
            self.dst_root = (args.root + os.path.sep).replace(os.path.sep*2, os.path.sep)
    
        if args.analyze:
            self.analyze =  True
    
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
                        self.codecs[templateid] =  CodecTemplate(templateid,templates[templateid]["opts"],templates[templateid]["container"])
            if 'ffmpeg' in d:
                self.ffmpeg = d["ffmpeg"]
            if 'temppath' in d:
                self.temppath = d["temppath"]
                self.logfile = self.temppath + os.path.sep + "actual.txt"
                self.task_list = self.temppath + os.path.sep + "list.txt"
            if 'extensions_filter' in d:
                self.exensions = tuple(d["extensions_filter"])
            if 'encode_identifiers' in d:
                self.encode_identifiers = tuple(d["encode_identifiers"])
            if 'ffprobe' in d:
                self.ffprobe = str(d["ffprobe"])
            if 'ffprobe_opts' in d:
                self.ffprobe_opts = str(d["ffprobe_opts"])