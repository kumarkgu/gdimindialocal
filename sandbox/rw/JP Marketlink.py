# --------- CODE STARTS HERE --------- #

import os
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from unipath import Path
from dotenv import load_dotenv


# Load settings
settings_file = Path(__file__).ancestor(1).child(".env")

if not settings_file.exists():
    raise RuntimeError(".env file does not exist")

load_dotenv(settings_file)

# Get user and password and secret question answer
try:
    USERNAME = os.environ["USERNAME"]
    PASS = os.environ["PASS"]
    SECRET_ANSWER = os.environ["SECRET_ANSWER"]
except KeyError as e:
    raise KeyError(e)


# noinspection PyBroadException
class Main:
    """Proof of concept for browser automation"""
    marketlink_url = "https://marketlink.jll.com/JLL/AP-Japan"
    property_name = "Prudential Tower"
    floor = 1
    unit = 1
    unit_rent = 100
    area = 100
    available_date = "2018/12/15"

    def __init__(self):
        """Launch chrome and visit MarketLink"""
        self.browser = webdriver.Chrome()
        self.browser.get(self.marketlink_url)
        self.login_okta()
        self.add_property()

    def login_okta(self):
        """Login to Okta verification"""
        # Wait until browser fully
        self.wait(By.ID, "txtUser")
        self.wait(By.ID, "txtPassword")

        email_input = self.browser.find_element_by_id("txtUser")
        pass_input = self.browser.find_element_by_id("txtPassword")
        form = self.browser.find_element_by_id("frmLogin")
        email_input.send_keys(USERNAME)
        pass_input.send_keys(PASS)
        form.submit()

        # Wait for secret answer
        self.wait(By.ID, "input39")

        secret_answer_input = self.browser.find_element_by_id("input39")
        secret_answer_input.send_keys(SECRET_ANSWER)
        secret_answer_input.submit()

    def add_property(self):
        """Add property in marketlink"""
        # Wait market link page to load
        while True:
            # noinspection PyBroadException
            try:
                self.browser.find_element_by_class_name("application-menu")
                break
            except Exception:
                print('Cannot find application-menu')
                time.sleep(2)
                continue

        # Click 物件
        self.find_and_click(
            "span[data-title=新規作成]", "新規作成"
        )
        self.find_and_click(
            "div.menu-item.tooltip.imageAndText.clickable", "物件"
        )

        # Fill in property
        input_fields = self.browser.find_elements_by_css_selector(
            "input[type=text]"
        )
        for field in input_fields:
            try:
                field.send_keys('THIS IS AN AUTOMATED INPUT')
            except Exception:
                continue

        time.sleep(3600)

    def find_and_click(self, selector, label):
        clickables = self.browser.find_elements_by_css_selector(selector)
        for i in clickables:
            print(i.text)
            if i.text == label:
                i.click()
                time.sleep(2)
                break
            else:
                continue

    def wait(self, by_obj: By, label: str):
        """
        Wait by class|id|tag|link_text|
        :param by_obj: By object
        :param label: element selector
        :return:
        """
        wait = WebDriverWait(self.browser, 10)
        wait.until(ec.visibility_of_element_located(
            (by_obj, label,),
        ))


if __name__ == "__main__":
    Main()
# --------- CODE ENDS HERE --------- #
