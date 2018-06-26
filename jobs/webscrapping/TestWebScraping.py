from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs
import time
import logging
import csv
import selenium

log = logging.getLogger("Web Scraping")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
log.addHandler(ch)


_DRIVER_PATH = "C:\\Users\\cyrus.fargose\\Downloads\\Old Downloads"
_CHROME_DRIVER = _DRIVER_PATH + "\\chromedriver.exe"
_IE_DRIVER = _DRIVER_PATH + "\\IEDriverServer.exe"
_CSV_PATH = "C:\\Users\\cyrus.fargose\\Documents\\PROJECTS\\Research_Rera\\UPRERA Mar18"
_CSV_FILE = _CSV_PATH + "\\UPRERA_URLs_Mar18.csv"
_WEB_SITE = "http://uprera.azurewebsites.net/projects"
_WEB_TOP_SITE = "http://uprera.azurewebsites.net/projects"
_CSV_HEADER = [
    "S.NO",
    "RegistrationNumber",
    "ProjectName",
    "Promoter",
    "District",
    "ProjectType"
    "Details",
    "ProjectID",
    "SummaryURL",
    "DetailsURL"
]

_DIST = ["Agra"]#,'Aligarh','Allahabaad','Amroha','Bahraich','Banda','Barabanki','Bareilly','Budaun','Bulandshahr','Chandauli','Etah','Etawah','Faizabad'
         #,'Firozabad','Gautam Buddha Nagar','Ghaziabad','Gorakhpur','Hamirpur','Hapur','Hardoi','Hathras','Jaunpur','Jhansi','Kanpur Dehat','Kanpur Nagar'
         #,'Kushinagar','Lakhimpur Kheri','Lalitpur','Lucknow','Mathura','Meerut','Moradabad','Muzaffarnagar','Pilibhit','Pratapgarh','Raebareli','Rampur'
         #,'Saharanpur','Sambhal','Shahjahanpur','Sitapur','Sonbhadra','Sultanpur','Unnao','Varanasi']

_SLEEP_TIME = 2

browser = wd.Chrome(_CHROME_DRIVER)
browser.get(_WEB_SITE)
#browser.maximize_window()
time.sleep(_SLEEP_TIME)



def select_district(district):
    try:
        __oSelDist = Select(
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_DdlprojectDistrict")
        )
        print(__oSelDist)
        __oSelDist.select_by_visible_text(district)

        time.sleep(_SLEEP_TIME)
    except Exception as e:#NoSuchElementException as e:
        log.info("District: {} does not exists".format(district))
        raise NoSuchElementException


# def get_page_properties(bsoup):
#     __oTable = bsoup.find(
#         'table',
#         attrs={'class': 'table table-striped grid-table'}
#     )
#     __oTBody = __oTable.find('tbody')
#     __oTRows = __oTBody.find_all('tr')
#     __lReturn = []
#     for __tRow in __oTRows:
#         __oTCols = __tRow.find_all('td')
#         __lTemp.append(__oTCols[0].get_text())
#         __lTemp.append(__oTCols[1].get_text())
#         __lTemp.append(__oTCols[2].get_text())
#         __lTemp.append(__oTCols[3].get_text())
#         __lTemp.append(__oTCols[4].get_text())
#         __lTemp.append(__oTCols[5].get_text())
#         __lReturn.append(__lTemp)
#
#     return __lReturn
#
#
# def get_page_details(bsoup, csvwriter):
#
#     __tHtml = None
#     __tSoup = None
#
#     __tSoup = bsoup
#
#     __lRecord = get_page_properties(__tSoup)
#     for __tRecord in __lRecord:
#         csvwriter.writerow(__tRecord)




try:
##    browser.find_element_by_xpath(
##        ".//*[contains(text(), 'Registered Projects')]"
##    ).click()
    # Now we got the element. Click on "Advanced Search button
    # But before that wait for 1 second to load
    # time.sleep(_SLEEP_TIME - 1)
##    browser.find_element_by_id("btnAdvance").click()
    # Now we got the element. Click on "Advanced Search button
    # But before that wait for 1 second to load
    # time.sleep(_SLEEP_TIME - 1)
    # Now division is loaded and hence select the required division
    with open(_CSV_FILE, 'w', newline='') as __oFD:
        __oWriter = csv.writer(
            __oFD,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )
        __oWriter.writerow(_CSV_HEADER)



        for __tDist in _DIST:
            # Now click Search
            __oHtml = None
            __oSoup = None
            log.info("..Procesing For District: {}".format(__tDist))
            __vReturn = select_district(district=__tDist)
            if __vReturn == -1:
                continue
            #browser.find_element_by_id("btnSearch").click()
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").send_keys(selenium.webdriver.common.keys.Keys.SPACE)
            time.sleep(_SLEEP_TIME)
            __oHtml = browser.page_source
            __oSoup = bs(__oHtml, "html.parser")
            
            # get_page_details(
            #     __oSoup,
            #     __oWriter,
            # )
    browser.close()
except Exception as e:#NoSuchElementException as e:
    browser.close()
    raise
except:#:
    browser.close()
    raise

log.info("Process Completed")
