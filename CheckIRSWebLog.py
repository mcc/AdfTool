import os
import sys

logdir = "D:\\Server_Log\\2016-07-10_11_12 PRD IRS\\Middleware Log\\Raw Log\\internet1_ohs1_20160719"

class LogAnalyzer():
    """ Parses and summarizes nginx logfiles """

    def __init__(self, readfile, writefile, topcount=50):
        """ Initializing """
        self.summary = {
            "requests": {},
            "ips": {}
        }

        self.topcount = topcount

        self.reafile = readfile
        self.writefile = writefile

    def analyze(self):
        """ Reads and splits the access-log into our dictionary """
        #is file?
        if not os.path.isfile(self.reafile):
            print(self.reafile, "does not exist! exiting")
            exit(1)

        log = open(self.reafile, 'r')
        lines = log.readlines()
        log.close()
        loglist = []

        for s in lines:
            line = s.strip()
            tmp = line.split(' ')
            ip = tmp[0]

            #not the finest way...get indices of double quotes
            doublequotes = LogAnalyzer.find_chars(line, '"')

            #get the starting/ending indices of request & useragents by their quotes
            request_start = doublequotes[0]+1
            request_end = doublequotes[1]
            #useragent_start = doublequotes[4]+1
            #useragent_end = doublequotes[5]

            request = line[request_start:request_end]
            #useragent = line[useragent_start:useragent_end]

            #writing a dictionary per line into a list...huh...dunno
            loglist.append({
                "ip": ip,
                "request": request,
#                "useragent": useragent
            })

        self.summarize(loglist)
        self.write_summary()

    def summarize(self, cols):
        """ count occurences """
        for col in cols:
            if not col['request'] in self.summary['requests']:
                self.summary['requests'][col['request']] = 0
            self.summary['requests'][col['request']] += 1

            if not col['ip'] in self.summary['ips']:
                self.summary['ips'][col['ip']] = 0
            self.summary['ips'][col['ip']] += 1

            #if not col['useragent'] in self.summary['useragents']:
            #    self.summary['useragents'][col['useragent']] = 0
            #self.summary['useragents'][col['useragent']] += 1

    def write_summary(self):
        """ sorts and writes occurences into file """
        summary = open(self.writefile, 'a')
        summary.write("Log summary of \n" + self.reafile)
        for key in self.summary:
            list = sorted(self.summary[key].items(), key=lambda x: x[1], reverse=True)
            list = list[:self.topcount]
            summary.write("\nTop "+key+":\n")
            for l in list:
                summary.write(l[0]+": "+str(l[1])+" times\n")
        summary.close()

    @staticmethod
    def find_chars(string, char):
        """ returns a list of all indices of char inside string """
        return [i for i, ltr in enumerate(string) if ltr == char]


if __name__ == '__main__':
    for folder, subs, files in os.walk(logdir):
        for filename in files:
            if "access" in filename:
                logfile = logdir + '\\access_log'
                summaryfile = './access_summary.log'
                summary = LogAnalyzer(os.path.join(folder, filename), summaryfile, 100)
                summary.analyze()