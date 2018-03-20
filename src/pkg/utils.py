import os,datetime,subprocess,sys,platform,json,config,shutil,locale
from os import system
Config = config.Configuration

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

    if py_version == 2:
        return raw_input(message)
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
    targetdir = os.path.dirname(target);
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    logger.warning("Copying " + source + " to " + target)
    shutil.copy(source, target)
    return

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