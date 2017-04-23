# encoding: utf-8
'''
Created on 10.04.2017

@author: Konstantin Czeller
'''

import sys,os,logging,shutil,argparse,platform,json,subprocess
from os import system

py_version = sys.version_info[0]
if py_version == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# logs the process here
FFMPEG="d:\\Tools\\ffmpeg-3.2.4-win64-shared\\bin\\ffmpeg.exe"
#FFMPEG="ffmpeg"
#TEMPPATH="/mnt/data/tmp"
TEMPPATH="C:\\tmp\\"
LOGFILE=TEMPPATH + os.path.sep + "actual.txt"
TEMPFILE="temp"
TASK_LIST=TEMPPATH + os.path.sep + "list.txt"

EXTENSIONS=('avi','mpg','mpeg','mpv','mp4','mkv','mov')
EXTRAOPTS="-v info -y -i"

LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

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
FORCE_ENCODE = False
PARANOID = False
DST_ROOT = ""
SRC_ROOT = ""
ANALYZE = False
ENCODE_IDENTIFIERS = ["xvid","mplayer"]

try:
    os.remove(LOGFILE)
    #os.remove(TEMPFILE)
    os.remove(TASK_LIST)
except (OSError) as e:
    print ("")  

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

def encode_test( codec, inputvideo, outputvideo ):
    return

def has_been_encoded(video, identifiers):
    codec_tag = get_codec_tag(video).lower()
    encoder = get_encoder(video).lower()
    if( any(identifier.lower() in codec_tag for identifier in identifiers) or any(identifier in encoder for identifier in identifiers) ):
        return True
    return False

def collect_videos(dir):
    collection = []
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
                    collection.append(full_file)
                    FILES.append(full_file)
    return collection

def get_tasklist():
    lst = []
    for file in FILES:
        for c in SELECTED_CODECS:
            targetfile = generate_output_path(file, c)
            if FORCE_ENCODE:
                lst.append(file + " - " + c + " (forced)")
                continue
            if not os.path.isfile(targetfile):
                lst.append(file + " - " + c)
    return lst

# prepare the output filenames and start the encoding
def process_folder( folder ):
    x = 0
    for c in SELECTED_CODECS:
        for file in FILES:
            x = x + 1
            set_window_title(str(x)  + "/" + str(len(FILES)) + " - " + file)
            process_video(c,file)

def process_video(codec, videofile):
    global FAILED_VIDEOS
    global FORCE_ENCODE
    
    targetfile = generate_output_path(videofile,codec)
    # file exists
    if os.path.isfile(targetfile) and  not FORCE_ENCODE:
        logger.error(targetfile + " has been already transcoded")
        return -1
    
    if PARANOID and any(os.path.isfile(generate_output_path(videofile,x)) for x in CODECS.keys()):
        logger.error(videofile + ' has been already transcoded with an other template, PARANOID mode is on')
        return -1 
    #        logger.error(videofile + " has been already transcoded with an other template!")
     #       return -2
    
    if FORCE_ENCODE: logger.warning("Forcing re-encode: " + videofile)
    
    ret = encode(codec,videofile)
    if ret == 0:
        logger.warning("done")
        olddate = os.path.getmtime(videofile)
        move_temp(get_temp_file(codec),targetfile, olddate)
    else:
        logger.warning("Failed to encode video: " + videofile + " - " + codec + " ret: " + str(ret))
        FAILED_VIDEOS.append(videofile)

def get_temp_file(template):
    ret = TEMPPATH + os.path.sep + TEMPFILE +'.' + CONTAINERS[template]
    print("TEMPFILE: " + ret)
    return ret

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
    global EXTENSIONS;
    global POSTS;
    global ANA
    
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
    command = "ffprobe -v error -select_streams v:0  -show_format -show_entries format=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret
    
def get_encoder(file):
    command = "ffprobe -v error -select_streams v:0 -show_entries stream=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

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
        
    global logger 
    logger = config_logger(LOGFILE)
    print("Selected codecs: ", SELECTED_CODECS)
    
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
        collection = collect_videos(inputParam)
        print_list(FILES,"Video List")
        my_input("Press a key to continue...")
        print_list(get_tasklist(),"Task List")
   #     my_input("Press a key to continue...")
  #      process_folder(inputParam)
 #       print_list(FAILED_VIDEOS,'Failed Videos')
        logger.error("Exit.")

main()