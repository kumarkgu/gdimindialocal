import time

from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from baselib.image.imagebase import imagebase as ip


# from bs4 import BeautifulSoup as bs


class BrowserOperation:
    def __init__(self, driverdir, chromerdriver=None, iedriver=None,
                 defaultdriver="Chrome", pathsep="/"):
        self._driver_path = driverdir + pathsep
        if chromerdriver:
            self._chromer_driver = self._driver_path + chromerdriver
        else:
            self._chromer_driver = self._driver_path + "chromedriver.exe"
        if iedriver:
            self._iedriver = self._driver_path + iedriver
        else:
            self._iedriver = self._driver_path + "IEDriverServer.exe"
        self.browser = self._set_browser(defaultdriver,
                                         chromedriver=self._chromer_driver,
                                         iedriver=self._iedriver)
        self.action_chains = ActionChains(self.browser)
        self.browser.maximize_window()

    def _set_browser(self, defaultdriver, chromedriver=None, iedriver=None):
        if defaultdriver == "Chrome":
            return wd.Chrome(chromedriver)
        else:
            return wd.Ie(iedriver)

    def get_browser(self):
        return self.browser

    def start_webpage(self, website, sleeptime=None):
        self.browser.get(website)
        if sleeptime:
            time.sleep(sleeptime)

    def close_broswer(self):
        if self.browser:
            self.browser.close()

    def right_click(self, actionobject=None, keys=None):
        self.action_chains.context_click(actionobject).send_keys(keys).perform()

    def take_screenshot(self, tagname, imagefile=None, **kwargs):
        try:
            __oimage = self.browser.find_elements_by_tag_name(tagname)
            if kwargs["itemno"]:
                __oimage = __oimage[kwargs["itemno"]]
            __vloc = __oimage.location
            __vsize = __oimage.size
            __vxcorr = kwargs.get("xcorr", 0)
            __vycorr = kwargs.get("ycorr", 0)
            __vwcorr = kwargs.get("widthcorr", 0)
            __vhcorr = kwargs.get("heightcorr", 0)
            __obox = (int(__vloc['x'] + __vxcorr),
                      int(__vloc['y'] + __vycorr),
                      int(__vloc['x'] + __vxcorr + __vsize["width"] + __vwcorr),
                      int(__vloc['y'] + __vycorr + __vsize["height"] + __vhcorr)
                      )
            __oscreenshot = self.browser.get_screenshot_as_base64()
            if imagefile:
                __oimage = ip.image_crop_save_base64(
                    __oscreenshot,
                    box=__obox,
                    filepath=imagefile
                )
            else:
                __oimage = ip.image_crop_save_base64(
                    __oscreenshot,
                    box=__obox
                )
        except NoSuchElementException:
            print("ERROR: Elements {} does not exists".format(tagname))
            raise
        except Exception as exc:
            raise

    def selectdata(self, idname, name, value=None):
        __oselect = Select(self.browser.find_element_by_id(idname))
        try:
            __oselect.select_by_visible_text(name)
        except NoSuchElementException:
            if value:
                __oselect.select_by_value(value)
            else:
                raise NoSuchElementException

    def inputdata(self, idname, inputtext, ifenter=False):
        try:
            __oidname = self.browser.find_element_by_id(idname)
            __oidname.send_keys(inputtext)
            if ifenter:
                __oidname.send_keys(Keys.ENTER)
        except NoSuchElementException:
            raise
        except Exception:
            raise