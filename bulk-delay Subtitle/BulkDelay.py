# Description: bulk-delay Subtitle of a srt file. 
# usage:  bulkDelay(OldSrt, NewSrt, Opp, time)
# OldSrt: the old Srt file Path
# NewSrt: the new Srt file Path
# Opp: "Add" or "Sub"
# time: the time to add/subtract

import re

# Helper: convert time to milliseconds
def TimeToMilliseconds(time):
    return int(time[0:2]) * 3600000 + int(time[3:5]) * 60000 + int(time[6:8]) * 1000 + int(time[9:])

# Helper: convert milliseconds to time
def MillisecondsToTime(ms):
    h = int(ms/3600000)
    hr = (ms % 3600000)
    m = int(hr/60000)
    hm = int(hr % 60000)
    s = int(hm/1000)
    ms = int(hm % 1000)
    if(h <= 9):
        h = "0"+str(h)
    if(m <= 9):
        m = "0"+str(m)
    if(s <= 9):
        s = "0"+str(s)
    if(ms <= 9):
        ms = "00"+str(ms)
    elif(ms <= 99):
        ms = "0"+str(ms)
    return f"{h}:{m}:{s},{ms}"

def addTwoTimes(basetime, addedtime):
    return MillisecondsToTime(TimeToMilliseconds(basetime)+TimeToMilliseconds(addedtime))

def subTwoTimes(basetime, subbedtime):
    if(basetime < subbedtime):
        return "Can't subtract two time subbedtime>basetime"
    return MillisecondsToTime(TimeToMilliseconds(basetime)-TimeToMilliseconds(subbedtime))

# Main function
def Adjust(OldTime, Time, Opp):
    if(Opp == "Add"):
        return addTwoTimes(OldTime[0:12], Time) + " --> " + addTwoTimes(OldTime[17:29], Time)
    elif(Opp == "Sub"):
        if(subTwoTimes(OldTime[0:12], Time) == None or subTwoTimes(OldTime[17:29], Time) == None):
            return None
        return subTwoTimes(OldTime[0:12], Time) + " --> " + subTwoTimes(OldTime[17:29], Time)

# Writing to a new file the same content but with different time (after the opp)
def bulkDelay(OldSrt, NewSrt, Opp, time):
    with open(OldSrt+".srt", 'rt') as fr:
        with open(NewSrt+".srt", 'wt') as fw:
            for Rline in fr.readlines():
                regex = "[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]"
                otime = re.findall(regex, Rline)
                if(len(otime) > 0):
                    fw.write(Adjust(otime[0], time, Opp) + "\n")
                else:
                    fw.write(Rline + "\n")
