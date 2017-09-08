# encoding: utf-8
'''
Created on 10.04.2017

@author: Konstantin Czeller
'''

import sys,os,logging,shutil,argparse,datetime,utils,config
from os import system
from config import Configuration
from utils import my_input, set_window_title, move_temp
from encstat import Statistics
from trans_logger import MyLogger
from classes import Videoo, Encoder

py_version = sys.version_info[0]
l = MyLogger('C:\\tmp\\logfile.txt',Configuration.log_date_format)

logger = l.getLogger()

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

def get_tasklist_report(videos):
    lst = []
    for video in videos:
        if video.existing:
            lst.append(video.origFile + " - " + video.codec.name + " (forced)")
            continue
        if not os.path.isfile(video.targetFile):
            lst.append(video.origFile + " - " + video.codec.name)
    return lst

# prepare the output filenames and start the encoding
# folder
def process_videos( videos, copy_only, stat ):
    failed_videos = []
    x = 0
    for video in videos:
        x = x + 1
        set_window_title(str(x)  + "/" + str(len(videos)) + " - " + video.origFile + "(" + video.codec.name + ")")
        if copy_only:
            utils.copy_file(video.origFile,video.targetFile)
        else:
            if( not process_video(video)):
                failed_videos.append(video.targetFile)
            stat.write_row(stat.generate_csv_row(video))

    return failed_videos

def process_video(video):
    tempfile = Configuration.temppath + os.path.sep + Configuration.tempfile + "." + video.codec.container
    encoder = Encoder(Configuration.logger, Configuration.ffmpeg, Configuration.extraopts, tempfile)
    if Configuration.paranoid and any(os.path.isfile(generate_output_path(videofile,x)) for x in CODECS.keys()):
        logger.error(videofile + ' has been already transcoded with an other template, PARANOID mode is on')
        video.setExecCode(0)
        return

    #        logger.error(videofile + " has been already transcoded with an other template!")
     #       return -2

    if video.forced: logger.warning("Forcing re-encode: " + video.origFile)

    video.setStartTime()
    ret = encoder.encode(video)
    video.setStopTime()
    video.setExecCode(ret)

    if ret == 0:
        logger.warning("done")
        olddate = os.path.getmtime(video.origFile)
        logger.warning("Moving '{}' -> '{}'".format(tempfile,video.targetFile))
        move_temp(tempfile ,video.targetFile, olddate)
        return True
    else:
        logger.warning("Failed to encode video: {} - {} ret: {}".format(video.origFile, video.codec.name, str(ret)))
        return False

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

def get_video_objs(files, src_root, dst_root, codecs, force):
    res = []
    for file in files:
        for codec in codecs:
            video = Videoo(file, src_root, dst_root, codecs[codec], force)
            if(force or (not video.existing)):
                res.append(video)
            else:
                print("Skipping: "+video.origFile)
    return res

def main():
    global logger
    config = Configuration('config.json')

    args = parse_arguments()
    config.process_args(args)

    inputParam = args.input
    print('Input: ' + inputParam)


    Configuration.logger = logger
    logger = config.logger
    print("Selected codecs: ", config.selected_codecs.keys())
    stats = Statistics(config.temppath + os.path.sep + "stats_" + datetime.datetime.now().strftime(config.statfile_name_date) + ".csv")

    posts = [ "_"+name for name in config.selected_codecs.keys()]
    posts.append("_enc")

    stat = Statistics(config.statfile)
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
        print(" - DEBUG - force: " + str(config.force_encode))
        videos = get_video_objs(unprocessed_files, config.src_root, config.dst_root, config.selected_codecs, config.force_encode)
        utils.print_list(get_tasklist_report(videos),"Task List", logger)
        my_input("Press a key to continue...")
        failed_videos = process_videos(videos, config.copy_only, stat)
        utils.print_list(failed_videos,'Failed Videos', logger)
        #write_stats(stats)
        logger.error("Exit.")

if __name__ == '__main__':
  main()
