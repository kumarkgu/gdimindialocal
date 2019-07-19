import csv
import re

def rewrite_file(infile, outfile=None, delimit=","):
    with open(infile, 'rt', encoding='utf-8') as incsv:
        if outfile:
            outcsv = open(outfile, 'wt', encoding='utf-8')
            outwriter = csv.writer(outcsv, delimiter=delimit)
        reader = csv.reader(incsv, dialect='excel', delimiter=delimit)
        for line in reader:
            outline = [field.replace("\n", " ") for field in line]
            if outfile:
                outwriter.writerow(outline)
            else:
                print(outline)
        if outfile:
            outcsv.close()


def _fill_to_list(rowlist, numberinsert):
    for intcounter in range(0, numberinsert):
        rowlist.insert(intcounter, "")


def arrange_csv(infile, outfile=None, pivotcol=None, pivotregexp=None,
                ignorecounter=None, multipage=False, fileno=None, headercol = 1):
    currcounter = 1
    with open(infile, 'rt', encoding='utf-8') as incsv:
        reader = csv.reader(incsv, dialect='excel')
        for line in reader:
            outline = [field.replace("\n", ";").rstrip() for field in line]
            if outline:
                if multipage and fileno > 1 and currcounter <= headercol:
                    currcounter += 1
                    continue
                if ignorecounter and currcounter > ignorecounter:
                    colcounter = 1
                    for curcol in outline[:]:
                        if pivotregexp.search(curcol):
                            if pivotcol > colcounter:
                                _fill_to_list(outline, pivotcol - colcounter)
                        colcounter += 1
                if outfile:
                    outfile.writerow(outline)
                else:
                    print(outline)
                currcounter += 1


def refill_csv(infile, outfile=None, ignorefirst=True):
    linecounter = 1
    if outfile:
        outcsv = open(outfile, 'wt', encoding='utf-8', newline="")
        writer = csv.writer(outcsv, delimiter=",")
    prevline = []
    with open(infile, 'rt', encoding='utf-8') as incsv:
        reader = csv.reader(incsv, dialect='excel')
        for line in reader:
            outline = [field for field in line]
            if linecounter == 1 and ignorefirst:
                pass
            else:
                try:
                    for posn in range(0, len(outline)):
                        if outline[posn] == "":
                            outline[posn] = prevline[posn]
                except IndexError:
                    pass
                prevline = outline
            linecounter += 1
            if outfile:
                writer.writerow(outline)
            else:
                print(outline)
        if outfile:
            outcsv.close()


def addxform(address):
    """
    Translate address 一丁目17番3号 into 1-17-3
    """

    if not address:
        return ''

    addtemp = str(address).replace(" ","").replace("‐","-").replace("番地","番")
    chomebangou = None
    chome = None
    ban = None
    gou = None

    numdict = {"一":"1",
               "二":"2",
               "三":"3",
               "四":"4",
               "五":"5",
               "六":"6",
               "七":"7",
               "八":"8",
               "九":"9",
               "十":"10"}

    #Capture number for 丁目
    if "丁目" in addtemp:
        chome_start = addtemp.find("丁目") - 1
        chome_end = addtemp.find("丁目") + 2
        chome = addtemp[chome_start:chome_start + 1]
        if chome in numdict:
            chomebangou = numdict[chome]
        else: chomebangou = str(chome)

    #Capture number for 番
    if re.search(r"\d+番", addtemp):
        banloc_start =  re.search(r"\d+番", addtemp).start()
        banloc_end = re.search(r"\d+番", addtemp).end()
        ban = addtemp[banloc_start:banloc_end - 1]
        if chomebangou:
            chomebangou = chomebangou + "-" + ban
        else: chomebangou = ban

    #Capture number for 号
    if re.search(r"\d+号", addtemp):
        gouloc_start = re.search(r"\d+号", addtemp).start()
        gouloc_end = re.search(r"\d+号", addtemp).end()
        gou = addtemp[gouloc_start:gouloc_end - 1]
        if chomebangou:
            chomebangou = chomebangou + "-" + gou
        else: chomebangou = gou

    if chome:
        start = chome_start
        if ban:
            if gou:
                #西中島5丁目13番14号
                end = gouloc_end
            else:
                #西中島5丁目13番
                end = banloc_end
                if re.search(r"\d+番\d", addtemp):
                    #西中島5丁目13番14
                    chomebangou = chomebangou + '-'
        else:
            if gou:
                #西中島5丁目14号
                end = gouloc_end
            else:
                #西中島5丁目
                end = chome_end
                if re.search(r"\d丁目\d", addtemp):
                    #西中島5丁目14
                    chomebangou = chomebangou + '-'
    else:
        if ban:
            start = banloc_start
            if gou:
                #西中島13番14号
                end = gouloc_end
            else:
                #西中島13番
                end = banloc_end
                if re.search(r"\d+番\d", addtemp):
                    #西中島13番14
                    chomebangou = chomebangou + '-'
        else:
            if gou:
                #西中島14号
                start = gouloc_start
                end = gouloc_end
            else:
                #西中島
                start = len(addtemp)
                end = len(addtemp)

    if chomebangou:
        addtemp = addtemp[:start] + chomebangou + addtemp[end:]

    return addtemp

#print(addxform("東京都千代田区六番町15-2"))


