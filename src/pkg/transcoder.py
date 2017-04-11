'''
Created on 10.04.2017

@author: Konstantin Czeller
'''

import sys,os,logging

# logs the process here
LOGFILE="c:\\tmp\\actual.txt"
TEMPFILE="c:\\tmp\\temp.mp4"
TASK_LIST="c:\\tmp\\list.txt"
SEARCHDIR="$1"
EXTENSIONS=('avi','mpg','mpeg','mpv','mp4','mkv')
FFMPEG="ffmpeg"
EXTRAOPTS="-v info -y"

SUBDIR="encode"
LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

CODECS = {}
CODECS["mp3"]="-c:v copy -c:a libmp3lame -q:a 5"
CODECS["x264"]="-c:v libx264 -preset veryslow -crf 20 -tune film -c:a aac -strict experimental -ab 128k -movflags faststart"
CODECS["x265"]="-c:v libx265 -preset slow -crf 20 -c:a aac -strict experimental -ab 128k -movflags faststart"

POSTS = ("enc","mp3","x264","x265")

FILES = []

if len(sys.argv) == 3:
    SELECTED_CODECS = sys.argv[2]
else:
    SELECTED_CODECS = ["x264", "x265","mp3"]

try:
    os.remove(LOGFILE)
    os.remove(TEMPFILE)
    os.remove(TASK_LIST)
except (OSError) as e:
    print ("")

def config_logger(logfile):
    logFormatter = logging.Formatter('%(asctime)s %(message)s',datefmt=LOG_DATE_FORMAT)
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.INFO)
    return rootLogger

def encode( codec, inputvideo, outputvideo ):
    return
def move_temp( target ):
    return

def encode_test( codec, inputvideo, outputvideo ):
    return

def collect_videos(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(EXTENSIONS):
                if  any(ext in file for ext in POSTS):
                    v=1 
                    #logger.warning("Skipping: "+os.path.join(root,file))
                else:
                    FILES.append(os.path.join(root,file))

# print/write out the found videos
def print_tasklist():
    for file in FILES:
            logger.info(file)

# prepare the output filenames and start the encoding
def process_folder( folder ):
    for c in SELECTED_CODECS:
        for file in FILES:
            process_video(c,file)

def process_video(codec, videofile):
    fname=os.path.splitext(os.path.basename(videofile))[0]+".mp4"
    targetdir=os.path.dirname(videofile)+os.path.sep+SUBDIR
    targetfile=os.path.join(targetdir,fname)
    
        

param1 = sys.argv[1]

print("Argument List:", str(sys.argv))
print("Selected codecs: ", SELECTED_CODECS)

logger = config_logger(LOGFILE)

if os.path.isfile(param1):
    logger.info("File processing: \""+param1+"\"")
    for c in SELECTED_CODECS:
        process_video(param1, c)

if os.path.isdir(param1):
    logger.info("Folder processing: "+param1)
    collect_videos(param1)
    print_tasklist()
    input("Press a key to continue...")
    process_folder(param1)