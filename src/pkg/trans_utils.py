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

def has_been_encoded(video, identifiers):
    #codec_tag = get_codec_tag(video).lower()
    #encoder = get_encoder(video).lower()
    video_details = get_video_details(video).lower()
    if(  any(identifier in video_details for identifier in identifiers) ):
        return True
    return False