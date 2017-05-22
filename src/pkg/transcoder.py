# encoding: utf-8
'''
Created on 10.04.2017

@author: Konstantin Czeller
'''

import sys,os,logging,shutil,argparse,platform,json,subprocess,datetime
from os import system

py_version = sys.version_info[0]
if py_version == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

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


try:
    os.remove(LOGFILE)
    #os.remove(TEMPFILE)
    os.remove(TASK_LIST)
except (OSError) as e:
    print ("")

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

def GetHumanReadableSize(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def config_logger(logfile):
    logFormatter = logging.Formatter('%(asctime)s %(message)s',datefmt=LOG_DATE_FORMAT)
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.INFO)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.WARNING)
    return rootLogger

def encode(codec, inputvideo):
    if codec not in CODECS.keys():
        logger.error("Unknown codec: "+codec)
        return -1
    encode_options = CODECS.get(codec)
    logger.warning("Transcoding "+inputvideo+" - "+codec)
    command = FFMPEG + " " + EXTRAOPTS + " \"" + inputvideo + "\" " + encode_options + " " + get_temp_file(codec)
    logger.error(command)
    ret = os.system(command)
    logger.warning("ret: "+str(ret))
    return ret

def move_temp( tempfile, target, date ):
    targetdir = os.path.dirname(target)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    logger.warning("Moving")
    shutil.move(tempfile,target)
    os.utime(target, (date, date))
    return

def copy_file(source, target):
    targetdir = os.path.dirname(target);
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    logger.warning("Copying " + source + " to " + target)
    shutil.copy(source, target)
    return

def encode_test( codec, inputvideo, outputvideo ):
    return

def has_been_encoded(video, identifiers):
    #codec_tag = get_codec_tag(video).lower()
    #encoder = get_encoder(video).lower()
    video_details = get_video_details(video).lower()
    if(  any(identifier in video_details for identifier in identifiers) ):
        return True
    return False

def collect_videos(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if str(file).lower().endswith(EXTENSIONS):
                full_file = os.path.join(root,file)
                if any(ext in file for ext in POSTS):
                    logger.error("Skipping - encoded file: "+full_file)
                    continue
                if ANALYZE and has_been_encoded(full_file, ENCODE_IDENTIFIERS):
                    logger.error("Skipping - analyzed as encoded file: " + full_file)
                else:
                    FILES.append(full_file)

def get_tasklist():
    lst = []
    for file in FILES:
        for c in SELECTED_CODECS:
            targetfile = generate_output_path(file, c)
            if FORCE_ENCODE and os.path.isfile(targetfile):
                lst.append(file + " - " + c + " (forced)")
                continue
            if not os.path.isfile(targetfile):
                lst.append(file + " - " + c)
    return lst

# prepare the output filenames and start the encoding
# folder
def process_folder( folder ):
    init_stats_file()
    x = 0
    for c in SELECTED_CODECS:
        for file in FILES:
            x = x + 1
            set_window_title(str(x)  + "/" + str(len(FILES)) + " - " + file)
            if COPY_ONLY:
                copy_file(file,generate_copy_outputpath(file))
            else:
                video = process_video(c,file)
                STATS.append(video)
                write_row(generate_csv_row(video))

def process_video(codec, videofile):
    global FAILED_VIDEOS
    global FORCE_ENCODE

    targetfile = generate_output_path(videofile,codec)
    video_object = Video(videofile, targetfile, codec)
    # file exists
    if os.path.isfile(targetfile) and  not FORCE_ENCODE:
        logger.error(targetfile + " has been already transcoded")
        video_object.setExecCode(0)
        return video_object

    if PARANOID and any(os.path.isfile(generate_output_path(videofile,x)) for x in CODECS.keys()):
        logger.error(videofile + ' has been already transcoded with an other template, PARANOID mode is on')
        video_object.setExecCode(0)
        return video_object

    #        logger.error(videofile + " has been already transcoded with an other template!")
     #       return -2

    if FORCE_ENCODE: logger.warning("Forcing re-encode: " + videofile)

    video_object.setStartTime()
    ret = encode(codec,videofile)
    video_object.setStopTime()
    video_object.setExecCode(ret)

    if ret == 0:
        logger.warning("done")
        olddate = os.path.getmtime(videofile)
        move_temp(get_temp_file(codec),targetfile, olddate)
    else:
        logger.warning("Failed to encode video: " + videofile + " - " + codec + " ret: " + str(ret))
        FAILED_VIDEOS.append(videofile)
    return video_object

def get_temp_file(template):
    ret = TEMPPATH + os.path.sep + TEMPFILE +'.' + CONTAINERS[template]
    print("TEMPFILE: " + ret)
    return ret

def generate_copy_outputpath(videofile):
    global DST_ROOT
    global SRC_ROOT
    if DST_ROOT:
        targetdir = videofile.replace(SRC_ROOT, DST_ROOT)
    return targetdir

def generate_output_path(videofile, codec):
    global DST_ROOT
    global SRC_ROOT
    fname = os.path.splitext(os.path.basename(videofile))[0]+"_" + codec + "." + CONTAINERS[codec]
    targetdir=os.path.dirname(videofile)+os.path.sep
    if not DST_ROOT:
        targetdir = targetdir + codec
    if DST_ROOT:
        targetdir = targetdir.replace(SRC_ROOT, DST_ROOT)
    ret = os.path.join(targetdir,fname)
    return ret

def parse_arguments():
    global DST_ROOT
    parser = argparse.ArgumentParser(description="Transcodes videos in a folder")
    parser.add_argument("-t","--templates", help="Available templates: " + str(list(CODECS.keys())))
    parser.add_argument("-i","--input", help="Input file/directory")
    parser.add_argument("-m","--temppath", help="Temp directory")
    parser.add_argument("-e","--encoder", help="Path to encoder binary")
    parser.add_argument("-s","--show", help="Show available encoding templates", action="count")
    parser.add_argument("-f","--force", help="Re-encode already encoded videos", action="count")
    parser.add_argument("-p","--paranoid", help="Paranoid skipping", action="count")
    parser.add_argument("-r","--root", help="Copies the encoded file into an other root folder")
    parser.add_argument("-a","--analyze", help="Analyze video formats", action="count")
    parser.add_argument("-c","--copy", help="copy files only, use it only with -r", action="count")
    args = parser.parse_args()

    if not args.input and not args.show:
        print("Input not found.")
        parser.print_help()
        sys.exit(2)
    return args

def cleanup_logs():
    try:
        os.remove(LOGFILE)
        os.remove(TEMPFILE)
        os.remove(TASK_LIST)
    except (OSError) as e:
        print ("")

def set_window_title(newTitle):
    systemType = platform.system()
    if systemType == "Linux":
        sys.stdout.write("\x1b]2;" + newTitle + "\x07")
    elif systemType == "Windows":
        system("title "+newTitle)

def my_input(message):
    py_version = sys.version_info[0]

    if py_version == 2:
        return raw_input(message)
    if py_version == 3:
        return input(message)

def read_config(file):
    global CODECS;
    global FFMPEG;
    global TEMPPATH
    global LOGFILE
    global TEMPFILE
    global TASK_LIST
    global EXTENSIONS
    global POSTS
    global FFPROBE
    global FFPROBE_OPTS

    with open(file) as data:
        d = json.load(data)
        if 'templates' in d:
            templates = d["templates"]
            if len(templates) > 0:
                CODECS.clear();
                for templateid in templates.keys():
                    CODECS[templateid] = templates[templateid]["opts"];
                    CONTAINERS[templateid] = templates[templateid]["container"];
            POSTS = list("_" + post for post in CODECS.keys())
            POSTS.append("_enc")
        if 'ffmpeg' in d:
            FFMPEG = d["ffmpeg"]
        if 'temppath' in d:
            TEMPPATH = d["temppath"]
            LOGFILE=TEMPPATH + os.path.sep + "actual.txt"
            TASK_LIST=TEMPPATH + os.path.sep + "list.txt"
        if 'extensions_filter' in d:
            EXTENSIONS = tuple(d["extensions_filter"])
        if 'encode_identifiers' in d:
            ENCODE_IDENTIFIERS = tuple(d["encode_identifiers"])
        if 'ffprobe' in d:
            FFPROBE = str(d["ffprobe"])
        if 'ffprobe_opts' in d:
            FFPROBE_OPTS = str(d["ffprobe_opts"])

def print_list(lst, title):

    if len(lst) > 0:
        max = 0
        for video in lst:
            if len(video) > max:
                max = len(video)
        max += 2
        if (max - len(title)) % 2 == 0: max += 1
        half = int((max - len(title)) / 2)
        logger.warning("-"*half + " "+title+" "+ "-"*half)
        for video in sorted(lst):
            logger.warning('| ' + video + ' '*(max-len(video)-2) + '|')
        logger.warning('-'*int(max+1))

def get_codec_tag(file):
    command = FFPROBE + " -v error -select_streams v:0  -show_format -show_entries format=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_encoder(file):
    command = FFPROBE + " -v error -select_streams v:0 -show_entries stream=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_video_details(file):
    command = str(FFPROBE) + " " + str(FFPROBE_OPTS) + " \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def write_stats(stats):
    init_stats_file()
    for video in STATS:
        write_row(generate_csv_row(video))

def write_row(row):
    stat_file = open(STATFILE, "a")
    stat_file.write(row)
    stat_file.close()

def init_stats_file():
    try:
        os.remove(STATFILE)
    except (OSError) as e:
        pass
    stat_file = open(STATFILE, "w")
    stat_file.write("Video file;" +
                    "Codec;" +
                    "Exec code;" +
                    "Start Time;" +
                    "End Time;" +
                    "Duration;" +
                    "Orig Size;" +
                    "Encoded Size;" +
                    "Orig;" +
                    "Encoded;" +
                    "Ratio\n")
    stat_file.close()

def generate_csv_row(video):
    ratio = os.path.getsize(video.targetPath) / os.path.getsize(video.sourcePath) * 100
    ratio = "{0:.2f}".format(ratio)
    ratio = ratio.replace('.',',')
    row = (video.sourcePath + ";" +
            video.codec+";" +
            str(video.execCode) + ";" + 
            video.getStartTime().strftime(LOG_DATE_FORMAT) + ";" + 
            video.getStopTime().strftime(LOG_DATE_FORMAT) + ";" + 
            str(video.getStopTime() - video.getStartTime()) + ";" + 
            str(os.path.getsize(video.sourcePath)) + ";" + 
            str(os.path.getsize(video.targetPath))+";" + 
            GetHumanReadableSize(os.path.getsize(video.sourcePath)) + ";" + 
            GetHumanReadableSize(os.path.getsize(video.targetPath)) + ";" + 
            str(ratio) + "\n")
    return row

def main():
    read_config('config.json')
    global SELECTED_CODECS
    global FFMPEG
    global EXTENSIONS
    global TEMPPATH
    global LOGFILE
    global TEMPFILE
    global TASK_LIST
    global FORCE_ENCODE
    global PARANOID
    global DST_ROOT
    global SRC_ROOT
    global ANALYZE
    global COPY_ONLY
    global STATFILE
    
    args = parse_arguments()

    inputParam = args.input
    print('Input: ' + inputParam)

    if args.temppath:
        TEMPPATH = args.temppath
        LOGFILE = TEMPPATH + os.path.sep + "actual.txt"
        TASK_LIST = TEMPPATH + os.path.sep + "list.txt"

    if args.encoder:
        FFMPEG = args.encoder

    if not args.templates:
        SELECTED_CODECS = CODECS.keys()
    else:
        SELECTED_CODECS = args.templates.split(",")
        WRONG_CODECS = []
        for codec in SELECTED_CODECS:
            if codec not in CODECS.keys():
                print("Unknown codec: " + str(codec))
                WRONG_CODECS.append(codec)
        for c in WRONG_CODECS:
            SELECTED_CODECS.remove(c)
        if not SELECTED_CODECS:
            print("")
            print("There is no known codec given.")
            print("Known codecs: " + str(CODECS.keys()))
            print("Exiting...")
            sys.exit(1)

    if args.show:
        print("Available templates")
        print("")
        for key in CODECS.keys():
            print(key+":    " + CODECS.get(key) + ' ('+CONTAINERS.get(key) + ')')
        print()
        print("FFMPEG: " + FFMPEG)
        print("TEMPPATH: " + TEMPPATH)
        print("EXTENSION FILTER: " + str(EXTENSIONS))
        print("POSTS: " + str(POSTS))
        sys.exit(1)

    if args.force:
        FORCE_ENCODE = True

    if args.paranoid:
        PARANOID = True

    if args.root:
        DST_ROOT = (args.root + os.path.sep).replace(os.path.sep*2, os.path.sep)

    if args.analyze:
        ANALYZE =  True

    if args.copy:
        if not args.root:
            print("With -c you must use -r!")
            print("Exiting...")
            sys.exit(1)
        COPY_ONLY = True

    global logger
    logger = config_logger(LOGFILE)
    print("Selected codecs: ", SELECTED_CODECS)

    STATFILE=TEMPPATH + os.path.sep + "stats_" + datetime.datetime.now().strftime(STATFILE_NAME_DATE) + ".csv"


    if not os.path.exists(inputParam):
        print(inputParam + ' does not exist...exiting')
        sys.exit(-1)

    if os.path.isfile(inputParam):
        logger.error("File processing: \""+inputParam+"\"")
        for c in SELECTED_CODECS:
            process_video(c, inputParam)

    if os.path.isdir(inputParam):
        inputParam = ((args.input + os.path.sep).replace(os.path.sep*2, os.path.sep))
        SRC_ROOT = inputParam
        logger.error("Folder processing: "+inputParam)
        collect_videos(inputParam)
        print_list(FILES,"Video List")
        my_input("Press a key to continue...")
        print_list(get_tasklist(),"Task List")
        my_input("Press a key to continue...")
        process_folder(inputParam)
        print_list(FAILED_VIDEOS,'Failed Videos')
        write_stats(STATS)
        logger.error("Exit.")

main()
