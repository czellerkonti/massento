# encoding: utf-8
'''
Created on 10.04.2017

@author: Konstantin Czeller
'''

import sys,os,logging,shutil,argparse,datetime,utils,config
from config import Configuration
from utils import my_input
from encstat import Statistics
from trans_logger import MyLogger
from classes import Videoo

py_version = sys.version_info[0]
l = MyLogger('C:\\tmp\\logfile.txt',Configuration.log_date_format)
logger = l.getLogger()

def encode_test( codec, inputvideo, outputvideo ):
    return

def collect_videos(dir, extensions, posts, encode_identifiers, analyze):
    res = []
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            
            if str(file).lower().endswith(extensions):
               
                full_file = os.path.join(root,file)
                
                if any(ext in file for ext in posts):
                    logger.error("Skipping - encoded file: "+full_file)
                    continue
                if analyze and has_been_encoded(full_file, encode_identifiers):
                    logger.error("Skipping - analyzed as encoded file: " + full_file)
                else:
                    res.append(full_file)
    
    return res

def get_tasklist(files, src_root, dst_root, codecs, force):
    lst = []
    for file in files:
        for codec in codecs:
            targetfile = generate_output_path(file, codec, src_root, dst_root)
            if force and os.path.isfile(targetfile):
                lst.append(file + " - " + codec.name + " (forced)")
                continue
            if not os.path.isfile(targetfile):
                lst.append(file + " - " + codec.name)
    return lst

# prepare the output filenames and start the encoding
# folder
def process_folder( files, selected_codecs, copy_only ):
    init_stats_file()
    x = 0
    for c in selected_codecs:
        for file in files:
            x = x + 1
            set_window_title(str(x)  + "/" + str(len(files)) + " - " + file)
            if cony_only:
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
    return

def parse_arguments():
    parser = argparse.ArgumentParser(description="Transcodes videos in a folder")
    parser.add_argument("-t","--templates", help="Available templates: " + str(list(Configuration.codecs.keys())))
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

def get_video_objs(files, src_root, dst_root, codecs):
    res = []
    for file in files:
        for codec in codecs:
            video = Videoo(file, src_root, dst_root, codecs)
            res.append(video)
    return res

def main():
    global logger
    config = Configuration('config.json')
    
    args = parse_arguments()
    config.process_args(args)
    
    inputParam = args.input
    print('Input: ' + inputParam)
    
    
    l = MyLogger(config.logfile,config.log_date_format)
    config.logger = l.getLogger()
    logger = config.logger
    print("Selected codecs: ", config.selected_codecs.keys())
    stats = Statistics(config.temppath + os.path.sep + "stats_" + datetime.datetime.now().strftime(config.statfile_name_date) + ".csv")
    
    posts = [ "_"+name for name in config.selected_codecs.keys()]
    posts.append("_enc")
    
    if not os.path.exists(inputParam):
        print(inputParam + ' does not exist...exiting')
        sys.exit(-1)

    if os.path.isfile(inputParam):
        logger.error("File processing: \""+inputParam+"\"")
        for c in config.selected_codecs:
            process_video(c, inputParam)

    if os.path.isdir(inputParam):
        inputParam = ((args.input + os.path.sep).replace(os.path.sep*2, os.path.sep))
        config.src_root = inputParam
        #logger.error("Folder processing: "+inputParam)
        unprocessed_files = collect_videos(inputParam, config.extensions, posts, config.encode_identifiers, config.analyze)
        utils.print_list(unprocessed_files,"Video List", logger)
        my_input("Press a key to continue...")
        videos = get_video_objs(unprocessed_files, config.src_root, config.dst_root, config.selected_codecs)
        utils.print_list(get_tasklist(unprocessed_files,
                                      config.selected_codecs, 
                                      config.src_root, 
                                      config.dst_root, 
                                      config.force_encode),
                         "Task List", logger)
        my_input("Press a key to continue...")
        process_folder(inputParam)
        print_list(FAILED_VIDEOS,'Failed Videos')
        write_stats(stats)
        logger.error("Exit.")

main()
