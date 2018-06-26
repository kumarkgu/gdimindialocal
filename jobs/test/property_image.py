import os
import glob
import re
import shutil


def clean_name(filename, regtest=None, regparan=None):
    modlist = []
    blnlast = False
    if regtest.search(filename):
        tname = regparan.sub('', filename)
        namelist = tname.split("_")
    else:
        namelist = filename.split("_")
    tname = ""
    for name in namelist:
        if name == "":
            continue
        tname = name.replace("'", "").replace("&", "")
        if name == namelist[-1]:
            if name.startswith("."):
                modlist[-1] = "{}{}".format(
                    modlist[-1],
                    name
                )
                blnlast = True
        if not blnlast:
            tname = tname.replace("-", "_")
            tname = tname.strip('_')
            if tname.upper() != "ID":
                tname = tname.capitalize()
            modlist.append(tname)
    tname = "_".join(modlist)
    tname = tname.replace("__", "_")
    tname = tname.replace("_.jpg", ".jpg")
    return tname
    # return modlist


def get_image_detail(filename, regtest=None, regparan=None):
    basefile = filename.rsplit('.', 1)
    fileext = filename.split(".")[-1]
    digital = {"FileType": fileext}
    # image_list = filename.split("_")
    tempname = clean_name(filename, regtest, regparan)
    image_list = tempname.split("_")
    digital["ObjectId"] = image_list[1]
    if image_list[2].upper() == "P":
        digital["IsPrimary"] = 1
    else:
        digital["IsPrimary"] = 0
    if image_list[2] == "F" or image_list[3] == "F":
        digital["DigitalAssetType"] = "Floor Plan"
    else:
        digital["DigitalAssetType"] = "Image"
    imagename = '{{}}\Box Sync\RetailAll\PropertyImage\{}'.format(tempname)
    digital["DigitalAssetLocalURL"] = imagename
    movefile = {
        "oldname": filename,
        "newname": tempname
    }
    return [digital, movefile]


def process_files(srcpath, commandfile):
    baseins = "INSERT INTO GDIMRegApac.IND_RET_STAGE.DigitalAsset ("
    baseins += "ObjectId,FileType,DigitalAssetType,DigitalAssetLocalURL,"
    baseins += "IsPrimary,ObjectType,IsDocument,RecordStatus,HistoryStartDate"
    baseins += ",HistoryEndDate,LoadedBy,UpdatedBy,LoadDate,UpdateDate"
    baseins += ") VALUES ("
    valuestr = "'Property',0,'Active','2010-01-01','9999-12-31','Gunjan.Kumar',"
    valuestr += "'Gunjan.Kumar',GETDATE(),GETDATE());"
    filenum = open(commandfile, "w")
    regparan = re.compile(r'\([^)]*\)')
    regtest = re.compile(r'\(')
    # movefile = []
    try:
        for filename in glob.glob(srcpath + "/*.*"):
            tempfile = os.path.basename(filename)
            print("..Processing File: {}".format(tempfile))
            retlist = get_image_detail(filename=tempfile, regtest=regtest,
                                       regparan=regparan)
            filedict = retlist[0]
            insertcmnd = "{0}{1},'{2}','{3}','{4}','{5}',{6}".format(
                baseins,
                filedict["ObjectId"],
                filedict["FileType"],
                filedict["DigitalAssetType"],
                filedict["DigitalAssetLocalURL"],
                filedict["IsPrimary"],
                valuestr
            )
            filenum.write(insertcmnd + '\n')
            srcfile = "{}/{}".format(srcpath, tempfile)
            destfile = "{}/{}".format(srcpath, retlist[1]["newname"])
            shutil.move(
                srcfile,
                destfile
            )
            # movefile.append(retlist[1])
        filenum.close()
        # print(movefile)
    except:
        filenum.close()
        raise


vuser = "C:/Users/gunjan.kumar"
vout = "{}/Documents/JLL/Projects/Retail/Forms/Version3/insert.mssql".format(
    vuser
)
vdir = "{}/Box Sync/RetailAll/PropertyImage".format(vuser)
process_files(vdir, vout)
