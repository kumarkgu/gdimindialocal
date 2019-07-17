from baselib.utils import base_util as bu
from tabula import convert_into
from baselib.image.imagetext import ReadImage

# from tabula import wrapper
# import json
# vmulti = 72
# dtable = {
#     "left": 0.47 * vmulti,
#     "right": 7.79 * vmulti
# }
# dtable0 = {
#     "top": 0.53 * vmulti,
#     "bottom": 1.87 * vmulti
# }
# dtable1 = {
#     "top": 2.6 * vmulti,
#     "bottom": 11.39 * vmulti
# }
# dtable2 = {
#     "top": 0.44 * vmulti,
#     "bottom": 11.39 * vmulti
# }
#
# vpath = "C:\\Users\\gunjan.kumar\\Documents\\JLL\\Projects\\Research\\IGR\\process\\bak_errorfiles"
# vname = "IGR2018_194_314"
# source = "{0}\\{1}.pdf".format(vpath, vname)
# # destination = "{0}\\{1}.json".format(vpath, vname)
# df = wrapper.read_pdf(
#     source, guess=False, stream=True, area="{0},{1},{2},{3}".format(
#         str(dtable1["top"]), str(dtable["left"]), str(dtable1["bottom"]),
#         str(dtable["right"])
#     ), pages="1"
# )
# js = json.loads(df.to_json(orient="records"))
# print(js)
#
# df = wrapper.read_pdf(
#     source, guess=False, stream=True, area="{0},{1},{2},{3}".format(
#         str(dtable2["top"]), str(dtable["left"]), str(dtable2["bottom"]),
#         str(dtable["right"])
#     ), pages="2"
# )
# js = json.loads(df.to_json(orient="records"))
# print(js)

vhome = "C:/Users/{}".format(bu.current_user())
vproject = "{0}/Documents/JLL/Projects/Research/IGR/process".format(vhome)
vtemp = "{}/temp/igr".format(vhome)
vfolder = "Fort"
vpath = "{0}/rawfiles/{1}".format(vproject, vfolder)
vname = "IGR2018_225_718"
#
#
# from baselib.image import imagetxt as it
#
# vpath = "C:/Users/gunjan.kumar/Documents/JLL/Projects/Research/IGR/process"
# vname = "bak_errorfiles-000001"
# source = "{0}\\{1}.png".format(vpath, vname)
#
#
# _OCR_PATH = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
#
#
# def _image_to_text(filename):
#     __oocr = it.ReadImage(_OCR_PATH)
#     __vvalue = __oocr.read_image(filename)
#     return __vvalue
#
#
# vtext = _image_to_text(source)
# print(vtext)


# source = "{0}\\{1}.pdf".format(vpath, vname)
# destination = "{0}\\{1}.json".format(vtemp, vname)
# convert_into(source, destination, output_format="json", guess=False)

vtess = "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe -c preserve_interword_spaces=1"
imgname = "{}/{}.png".format(vtemp, vname)
oimage = ReadImage(vtess)
vtext = oimage.read_image(imgname)
print(vtext)

# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from io import StringIO
#
# def pdf_to_text(pdfname):
#     # PDFMiner boilerplate
#     rsrcmgr = PDFResourceManager()
#     sio = StringIO()
#     codec = 'utf-8'
#     laparams = LAParams()
#     device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
#     interpreter = PDFPageInterpreter(rsrcmgr, device)
#     # Extract text
#     fp = open(pdfname, 'rb')
#     for page in PDFPage.get_pages(fp):
#         interpreter.process_page(page)
#     fp.close()
#     # Get text from StringIO
#     text = sio.getvalue()
#     # Cleanup
#     device.close()
#     sio.close()
#     return text
#
# vtext = pdf_to_text(source)
# print(vtext)


# import PyPDF2
# opdffile = open(source, 'rb')
# pdfreader = PyPDF2.PdfFileReader(opdffile)
# for i in range(0, pdfreader.numPages):
#     print("Current Page Number: {}".format(str(i)))
#     pageObj = pdfreader.getPage(1)
#     # pageObj = pdfreader.getPage(1)
#     print(pageObj.extractText())
# # print(pageObj.extractText())
# opdffile.close()
