import os,datetime,subprocess,sys,platform,json,config
from os import system
Config = config.Configuration


def get_video_details(file):
    command = str(Config.FFPROBE) + " " + str(Config.FFPROBE_OPTS) + " \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_codec_tag(file):
    command = Config.FFPROBE + " -v error -select_streams v:0  -show_format -show_entries format=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def get_encoder(file):
    command = Config.FFPROBE + " -v error -select_streams v:0 -show_entries stream=codec_tag_string -of default=noprint_wrappers=1 \"" + file + "\""
    ret = subprocess.check_output(command, shell=True)
    ret = str(ret)
    ret = ret.replace('\n', '').replace('\r', '')
    #print(ret)
    return ret

def GetHumanReadableSize(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def has_been_encoded(video, identifiers):
    #codec_tag = get_codec_tag(video).lower()
    #encoder = get_encoder(video).lower()
    video_details = get_video_details(video).lower()
    if(  any(identifier in video_details for identifier in identifiers) ):
        return True
    return False

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
    with open(file) as data:
        d = json.load(data)
        if 'templates' in d:
            templates = d["templates"]
            if len(templates) > 0:
                Config.CODECS.clear();
                for templateid in templates.keys():
                    Config.CODECS[templateid] = templates[templateid]["opts"];
                    Config.CONTAINERS[templateid] = templates[templateid]["container"];
            POSTS = list("_" + post for post in Config.CODECS.keys())
            POSTS.append("_enc")
        if 'ffmpeg' in d:
            Config.FFMPEG = d["ffmpeg"]
        if 'temppath' in d:
            Config.TEMPPATH = d["temppath"]
            Config.LOGFILE=Config.TEMPPATH + os.path.sep + "actual.txt"
            Config.TASK_LIST=Config.TEMPPATH + os.path.sep + "list.txt"
        if 'extensions_filter' in d:
            Config.EXTENSIONS = tuple(d["extensions_filter"])
        if 'encode_identifiers' in d:
            Config.ENCODE_IDENTIFIERS = tuple(d["encode_identifiers"])
        if 'ffprobe' in d:
            Config.FFPROBE = str(d["ffprobe"])
        if 'ffprobe_opts' in d:
            Config.FFPROBE_OPTS = str(d["ffprobe_opts"])