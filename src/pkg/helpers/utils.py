import os,datetime,subprocess,sys,platform,json,shutil,locale, re
from os import system
from helpers.config import Configuration

logger = Configuration.logger

def GetHumanReadableSize(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def set_window_title(newTitle):
    systemType = platform.system()
    if systemType == "Linux":
        sys.stdout.write("\x1b]2;" + newTitle + "\x07")
    elif systemType == "Windows":
        system("title "+newTitle)
        
def my_input(message):
    py_version = sys.version_info[0]

    #if py_version == 2:
    #    return raw_input(message)
    if py_version == 3:
        return input(message)
    
def move_temp( tempfile, target, date ):
    targetdir = os.path.dirname(target)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    shutil.move(tempfile,target)
    os.utime(target, (date, date))
    return

def copy_file(source, target):
    targetdir = os.path.dirname(target)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    logger.warning("Copying " + source + " to " + target)
    shutil.copy(source, target)

def print_list(lst, title, logger):
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
            #video = video
            logger.warning('| ' + video + ' '*(max-len(video)-2) + '|')
        logger.warning('-'*int(max+1))
        
def get_video_details(file):
    command = str(Configuration.ffprobe) + " " + str(Configuration.ffprobe_opts) + " \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_codec_tag(file):
    command = Configuration.ffprobe + " -v error -select_streams v:0  -show_format -show_entries format=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_encoder(file):
    command = Configuration.ffprobe + " -v error -select_streams v:0 -show_entries stream=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def has_been_encoded(video, identifiers):
    #codec_tag = get_codec_tag(video).lower()
    #encoder = get_encoder(video).lower()
    video_details = get_video_details(video).lower()
    if(  any(identifier in video_details for identifier in identifiers) ):
        return True
    return False

def get_video_width(file):
    command = str(Configuration.ffprobe) + " " + str(Configuration.ffprobe_width) + " " + "\"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    result = re.sub('[^0-9]','', ret.split("=")[-1])
    return int(result)