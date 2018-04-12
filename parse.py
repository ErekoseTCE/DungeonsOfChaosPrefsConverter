import sys
import pprint

columnDeltas = [0]
cdlen = 1

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def makeColumnDeltas(specialTag):
    columnDeltas = []
    for v in specialTag:
        columnDeltas.append(ord(v)-4);
    columnDeltas.append(0x32);
    return columnDeltas


def docDecode(bytearr, specialTag):
    cd = makeColumnDeltas(specialTag)
    cdlen = len(cd)
    blen = len(bytearr)
    idx = 0;
    col = 0;
    ret = ""
    while idx < blen:
        v = bytearr[idx];
        if  v < 0x80:
            v = v - cd[col%cdlen]
        else:
            v = bytearr[idx+1] - cd[col%cdlen];
            idx += 1;

        ret += chr(v);
        col += 1
        idx += 1
    return ret


def docEncode(bytearr, specialTag):
    cd = makeColumnDeltas(specialTag)
    cdlen = len(cd)
    blen = len(bytearr)
    idx = 0;
    col = 0;
    ret = ""
    while idx < blen:
        v = bytearr[idx]+cd[col%cdlen];
        if  v > 0x7F:
            ret += chr(0xc2)

        ret += chr(v)
        col += 1
        idx += 1
    return ret


def createAchievmentRecords(alist, specialTag):
    achievement_arr = []
    for achievement in alist:
        bytearr = bytearray(achievement)
        if is_ascii(achievement):
            text = achievement
            blob = docEncode(bytearr, specialTag)
        else:
            text = docDecode(bytearr, specialTag)
            blob = achievement
        achievement_arr.append({'text' : text, 'blob' : blob})

    prefs_dict['DoC_achievements']['array'] = achievement_arr
    if is_ascii(achieveBlob):   # The source file was Android cause the achievements are in plaintext
        # There for the ['data'] field is already correct (nominally plaintext)
        prefs_dict['DoC_achievements']['blob'] = "@".join(c['blob'] for c in achievement_arr)
    else:
        prefs_dict['DoC_achievements']['blob'] =  prefs_dict['DoC_achievements']['data']
        prefs_dict['DoC_achievements']['data'] = "@".join(c['text'] for c in achievement_arr)
    
    
############   Main   ##############

filename = sys.argv[1]
output = "mac"
if len(sys.argv) > 2 and sys.argv[2] == "-m":
    output = "mac"
if len(sys.argv) > 2 and sys.argv[2] == "-a":
    output = "android"
if len(sys.argv) > 2 and sys.argv[2] == "-d":
    output = "debug"
if len(sys.argv) > 2 and sys.argv[2] == "-r":
    output = "readable"


with open(filename, 'r') as myfile: data=myfile.read()

prefs_dict = {}
filePos = 0
for pref in data.split(';'):
    prefFields = pref.split(':')
    prefs_dict[prefFields[0].strip()] = { 'data' : prefFields[1].strip(), 'type' : prefFields[2].strip() }
    filePos += 1

achieveBlob = prefs_dict['DoC_achievements']['data']

achievement_list = achieveBlob.split('\x40')

specialTag = prefs_dict['DoC_specialtag']['data']
createAchievmentRecords(achievement_list, specialTag)

if output == "debug":
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(prefs_dict)

if output == "readable":
    for k in sorted(prefs_dict.keys()):
        if "array" in prefs_dict[k]:
            print("%s : %s" % (k, prefs_dict[k]['array'][0]['text']))
            for i,v in enumerate(prefs_dict[k]['array']):
                if i != 0:
                    print("     %s" % (v['text'])) 
        else:
            print("%s : %s" % (k, prefs_dict[k]['data']))

if output == "android" or output == "both":
    o = []
    prefs_dict['DoC_specialtag']['data'] = ""
    for k in prefs_dict.keys():
        if k == "DoC_achievements":
            o.append(" : ".join([k, prefs_dict[k]['data'], prefs_dict[k]['type']]))
        else:
            o.append(" : ".join([k, prefs_dict[k]['data'], prefs_dict[k]['type']]))
    print " ; ".join(o);
    specialTag = prefs_dict['DoC_specialtag']['data']

if output == "mac" or output == "both":
    if len(specialTag) == 0:
        specialTag =  prefs_dict['DoC_specialtag']['data'] = "12345"
        createAchievmentRecords(achievement_list, specialTag)
    o = []
    for k in prefs_dict.keys():
        if k == "DoC_achievements":
            o.append(" : ".join([k, prefs_dict[k]['blob'], prefs_dict[k]['type']]))
        else:
            o.append(" : ".join([k, prefs_dict[k]['data'], prefs_dict[k]['type']]))
    print " ; ".join(o);


