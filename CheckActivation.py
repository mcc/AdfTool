import os
import re
import dateutil.parser
import datetime
from pytz import timezone
import csv


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry

fmt = "%Y/%m/%d %H:%M:%S"
path = "D:\\Server_Log\\Prod_DTS1_2016_08_16\\"
user_logs = dict()
csvfile = open('activation_log.csv', 'w', newline='')
csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"')
line_pat = re.compile(r"\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]*)\] \[([^\]]+)\] \[tid\: \[([^\]]+)\][^]]*\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] (.*)")
exec_at_pat = re.compile(r".*Executed at (\d+/\d+/\d+ \d+\:\d+:\d+).*")
last_chk_at_pat = re.compile(r".*Attended on or after (\d+/\d+/\d+ \d+\:\d+:\d+).*")
hkt = timezone('Asia/Hong_Kong')
activation_prefix_str = " [CIMS_CHECK] activation occurs, ApplicationModuleName"
activation_postfix_str = ", if it happen frequently, consider to adjust the application module config"
for entry in scantree(path):
    #we only look for archived log, that is app-dts2-diagnostic-*.log
    if not entry.name.startswith('app-dts1-diagnostic-') or not entry.is_file() or not entry.name.endswith('log'):
        continue
    print("Processing: " + entry.path)
    file = open(entry.path, encoding='UTF-8')
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    line = file.readline()
    for line in open(entry.path).readlines():
        if (line_pat.match(line)):
            search_result = line_pat.search(line)
            username = search_result.group(7)
            logtime = dateutil.parser.parse(search_result.group(1))
            session_id = search_result.group(8)
            log_msg = search_result.group(10)
            diff = 0

            if (  activation_prefix_str in log_msg ):
                csvwriter.writerow([logtime, log_msg[len(activation_prefix_str): len(log_msg) - len(activation_postfix_str)], ])
            #print([username]  + ", " + session_id + ", " + log_msg)
            #print(line)
    #print(user_logs['userId: CHK_PRD_DTS-2'])
    file.close()
csvfile.close()