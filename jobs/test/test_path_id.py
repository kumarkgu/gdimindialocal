import os
import glob
import re
from baselib.utils import Logger as lo
from baselib.utils import fileobjects as fo

log = lo.Logger("Image").getlog()


def get_id_building(path):
    filedict = {}
    filereg = re.compile(r'^([\S\s]*\S)\s*-\s*ID\s*-\s*(\d+)', re.IGNORECASE)
    for filename in glob.glob(path + "/*.*"):
        basefile = os.path.basename(filename)
        filewoext = basefile.rsplit('.', 1)[0]
        regmatch = filereg.search(filewoext)
        if regmatch:
            buildingname = regmatch.group(1)
            buildingid = regmatch.group(2)
            filedict[buildingid] = buildingname
        else:
            print("No Matching String. {}".format(filename))
    return filedict


def prepare_insert(path):
    filedict = get_id_building(path=path)
    basestrn = "INSERT INTO #TEMP_IMAGE (BuildingId, BuildingName) VALUES "
    basestrn += "({0}, '{1}')"
    colonreg = re.compile(r"'")
    # insertlst = []
    for key, value in filedict.items():
        # insertlst.append(basestrn.format(str(key), value))
        regmatch = colonreg.search(value)
        if regmatch:
            value = value.replace("'", "''")
        print(basestrn.format(str(key), value))
    # return insertlst


def proper_case(string, regcheck, regsubs):
    filename = string
    if regcheck.search(string):
        filename = regsubs.sub('', string).replace("__", "_").strip("_")
    propcase = [x.capitalize() for x in filename.split("_")]
    filename = "_".join(propcase)
    return  filename


def rename_images(srcpath, destpath):
    regex = re.compile(r'([\S\s\-]+)(ID)([\s\-_]+)(\d+)(\D*)')
    regtest = re.compile(r'\(')
    regparan = re.compile(r'\([^)]*\)')
    propid = {}
    for filename in glob.glob(srcpath + "/*.*"):
        basefile = os.path.basename(filename)
        fileext = basefile.split(".")[-1]
        fileext = "" if basefile == fileext else "." + fileext
        regmatch = regex.search(basefile)
        if regmatch:
            idnumber = regmatch.group(4)
            if idnumber in propid:
                currlength = len(propid[idnumber]) + 1
            else:
                currlength = 1
            newfile = regmatch.group(1).strip()
            newfile = newfile.replace(".", "").replace("&", "")
            newfile = newfile.replace(" ", "_").replace("_-_", "_").strip("_-")
            newfile = proper_case(newfile, regtest, regparan)
            if currlength == 1:
                newfile = "ID_{}_P_{}_{}{}".format(
                    idnumber, newfile, currlength, fileext
                )
                propid[idnumber] = [newfile]
            else:
                newfile = "ID_{}_{}_{}{}".format(
                    idnumber, newfile, currlength, fileext
                )
                propid[idnumber].append(newfile)

        else:
            newfile = basefile.replace(".", "").replace("&", "")
            newfile = newfile.replace(" ", "_").replace("_-_", "_").strip("_-")
            print("....No Match")
        log.info("Copying File: {} To {}".format(basefile, newfile))
        # log.info("Base File: {}. Renamed File: {}".format(basefile, newfile))
        fo.copy_file(filename, destpath + "/" + newfile)


vsrcpath = "C:/Users/gunjan.kumar/Box Sync/RetailAll/Property Images"
vdestpath = "C:/Users/gunjan.kumar/Box Sync/RetailAll/RenamedImage"
rename_images(vsrcpath, vdestpath)
# prepare_insert(vpath)

