import os,codecs
from helpers.config import Configuration
from helpers.utils import *

class Statistics:
         
    def __init__(self, statfile):
        
        self.statfilepath = statfile
        try:
            os.remove(self.statfilepath)
        except (OSError) as e:
            pass
        self.stat_file = codecs.open(self.statfilepath, "w", "utf-8")
        self.stat_file.write("Video file;" +
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
        self.stat_file.close()
        
    def write_row(self,row):
        self.stat_file = codecs.open(self.statfilepath, "a", "utf-8")
        self.stat_file.write(row)
        self.stat_file.close()    
    
    def generate_csv_row(self,video):
        targetSize = 0
        ratio = 0
        origSize = os.path.getsize(video.origFile)
        if(os.path.exists(video.targetFile)):
            ratio = os.path.getsize(video.targetFile) / os.path.getsize(video.origFile) * 100
            targetSize = os.path.getsize(video.targetFile)
            
        ratio = "{0:.2f}".format(ratio)
        ratio = ratio.replace('.',',')
        row = (video.origFile + ";" +
                video.codec.name+";" +
                str(video.execCode) + ";" + 
                video.getStartTime().strftime(Configuration.log_date_format) + ";" + 
                video.getStopTime().strftime(Configuration.log_date_format) + ";" + 
                str(video.getStopTime() - video.getStartTime()) + ";" + 
                str(origSize) + ";" + 
                str(targetSize)+";" + 
                GetHumanReadableSize(origSize) + ";" + 
                GetHumanReadableSize(targetSize) + ";" + 
                str(ratio) + "%\n")
        return row
    
    def write_stats(self,stats):
        for video in stats:
            write_row(generate_csv_row(video))