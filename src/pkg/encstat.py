import os,utils,config
config = config.Configuration

class Statistics:
         
    def __init__(self, statfile):
        
        self.statfilepath = statfile
        try:
            os.remove(self.statfilepath)
        except (OSError) as e:
            pass
        self.stat_file = open(self.statfilepath, "w")
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
        self.stat_file = open(self.statfilepath, "a")
        self.stat_file.write(row)
        self.stat_file.close()    
    
    def generate_csv_row(self,video):
        ratio = os.path.getsize(video.targetPath) / os.path.getsize(video.sourcePath) * 100
        ratio = "{0:.2f}".format(ratio)
        ratio = ratio.replace('.',',')
        row = (video.sourcePath + ";" +
                video.codec+";" +
                str(video.execCode) + ";" + 
                video.getStartTime().strftime(config.LOG_DATE_FORMAT) + ";" + 
                video.getStopTime().strftime(config.LOG_DATE_FORMAT) + ";" + 
                str(video.getStopTime() - video.getStartTime()) + ";" + 
                str(os.path.getsize(video.sourcePath)) + ";" + 
                str(os.path.getsize(video.targetPath))+";" + 
                utils.GetHumanReadableSize(os.path.getsize(video.sourcePath)) + ";" + 
                utils.GetHumanReadableSize(os.path.getsize(video.targetPath)) + ";" + 
                str(ratio) + "\n")
        return row
    
        def write_stats(self,stats):
            for video in stats:
                write_row(generate_csv_row(video))