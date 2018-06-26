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
                ignorecounter=None, multipage=False, fileno=None):
    currcounter = 1
    with open(infile, 'rt', encoding='utf-8') as incsv:
        reader = csv.reader(incsv, dialect='excel')
        for line in reader:
            outline = [field.replace("\n", ";").rstrip() for field in line]
            if outline:
                if multipage and fileno > 1 and currcounter == 1:
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
