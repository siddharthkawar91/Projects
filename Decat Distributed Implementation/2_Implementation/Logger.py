import time
import datetime

class Logger:
    def __init__(self, filename):
        self.filename = filename
        file = open(filename, "w")
        file.truncate()
        file.close()
    
    def write(self, line: str):
        file = open(self.filename, 'a')
        file.write("[" + self.getTimestamp() + "]")
        file.write(" ")
        file.write(line)
        file.write('\n')
        file.close()

    def getTimestamp(self):
        ts = time.time()
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S')