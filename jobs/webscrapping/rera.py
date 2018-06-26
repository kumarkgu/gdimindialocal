import csv
import time
from base.utils import base_util as bu
from base.websuite import setbrowser as sb
from base.utils.Logger import Logger


_PATH_SEP = bu.get_path_separator()
_DRIVER_PATH = "C:\\Users\\gunjan.kumar\\Documents\\Drivers"
_CHROME_DRIVER = "chromedriver.exe"
_IE_DRIVER = "IEDriverServer.exe"
_CSV_PATH = "C:\\Users\\gunjan.kumar\\Documents\\JLL\\Projects\\Research\\RERA"
_CSV_FILE = _CSV_PATH + "\\maharashtra_rera_test.csv"
_WEB_SITE = "https://maharerait.mahaonline.gov.in/SearchList/Search"
_WEB_TOP_SITE = "https://maharerait.mahaonline.gov.in"
_SLEEP_TIME = 2

_CSV_HEADER = [
    "Division",
    "District",
    "Total Records",
    "Current Record Number",
    "Property Name",
    "Developer Name",
    "Website"
]

_MAHA_DIV_DIST = {
    "Amravati": [
        "Akola",
        "Amravati",
        "Buldana",
        "Washim",
        "Yavatmal"
    ],
    "Aurangabad": [
        "Aurangabad",
        "beed",
        "Hingoli",
        "Jalna",
        "Latur",
        "Nanded",
        "Osmanabad",
        "Parbhani"
    ],
    "Konkan": [
        "Mumbai City",
        "Mumbai Suburban",
        "Palghar",
        "Raigarh",
        "Ratnagiri",
        "Sindhudurg",
        "Thane"
    ],
    "Nagpur": [
        "Bhandara",
        "Chandrapur",
        "Gadchiroli",
        "Gondiya",
        "Nagpur",
        "Wardha"
    ],
    "Nashik": [
        "Ahmednagar",
        "Dhule",
        "Jalgaon",
        "Nandurbar",
        "Nashik"
    ],
    "Pune": [
        "Kolhapur",
        "Pune",
        "Sangli",
        "Satara",
        "Solapur"
    ]
}

log = Logger("Rera Data").getlog()


def _select_div_dist(browser, idname, divdistname):
    __vreturn = 0
    try:
        sb.selectdata(browser, idname, divdistname)
    except Exception as e:
        __vreturn = -1
    return __vreturn


def _process_rera(browser, csvfile, division, csvheader=None):
    with open(csvfile, 'w', newline='') as __ofd:
        __owriter = csv.writer(
            __ofd,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )
        if csvheader:
            __owriter.writerow(csvheader)
        for __tdiv, __ldist in division.items():
            log.info("Processing For Division {}".format(__tdiv))
            __vreturn = _select_div_dist(browser, "Division", __tdiv)
            if __vreturn == -1:
                log.info("..WARNNING: Division {} Does Not Exists. "
                         "Continue WIth Next Division".format(__tdiv))
                continue
            for __tdist in __ldist[:]:
                log.info("..Processing For District {}".format(__tdist))
                __vreturn = _select_div_dist(browser, "District", __tdist)
                if __vreturn == -1:
                    log.info("....WARNNING: District {} Does Not Exists. "
                             "Continue WIth Next Division".format(__tdist))
                    continue
                browser.find_element_by_id("btnSearch").click()


def process_maha_rera(website, division=_MAHA_DIV_DIST,  sleeptime=None,
                      driver_path=_DRIVER_PATH, default_driver="Chrome",
                      chromedriver=_CHROME_DRIVER, iedriver=_IE_DRIVER,
                      csvfile=_CSV_FILE, csvheader=_CSV_HEADER,
                      pathsep=_PATH_SEP):
    log.info("Starting to Process RERA Data from Website: " + website)
    __obrsrobj = sb.BrowserOperation(driver_path,chromerdriver=chromedriver,
                                     pathsep=pathsep)
    __obrsrobj.start_webpage(website, sleeptime=sleeptime)
    __obrowser = __obrsrobj.get_browser()
    try:
        __obrowser.find_element_by_xpath(
            ".//*[contains(text(), 'Registered Projects')]"
        ).click()
        __obrowser.find_element_by_id("btnAdvance").click()
    except Exception as e:
        log.info("ERROR: While Processing RERA Dara")
        log.info(e)
    finally:
        log.info("Closing Browser and exiting")
        __obrsrobj.close_broswer()

if __name__ == '__main__':
    vwebsite = _WEB_SITE
    process_maha_rera(vwebsite)
