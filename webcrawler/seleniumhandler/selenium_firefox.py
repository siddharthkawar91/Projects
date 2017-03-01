from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from lxml.html.clean import Cleaner
from lxml.html import fromstring
from lxml import etree
import time
from bs4 import BeautifulSoup
import sys


class SeleniumFirefox(object):

    def __init__(self, task_obj, worker_name):

        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.task_obj = task_obj
        self.browser_name = "firefox"

        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        ippor = self.get_proxy_server(worker_name)
        profile.set_preference("network.proxy.http", ippor[0])
        profile.set_preference("network.proxy.http_port", ippor[1])
        profile.update_preferences()

        # self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary('/usr/bin/firefox'), timeout=150,
        #                                     proxy=self.set_firefox_proxy(worker_name))
        self.driver = webdriver.Firefox(firefox_profile=profile)

        try:
            self.fetch_url(task_obj)
        except TimeoutException:
            print "time out occurred"
            pass

        self.visible_text = self.driver.page_source
        self.driver.quit()
        self.visible_text = self.get_visible_text(self.visible_text)
        self.task_obj.visible_text = self.visible_text
        self.display.stop()

    def set_firefox_proxy(self, worker_name):
        # pro = self.get_proxy_server(worker_name)
        print "Firefox : "
        # proxy = Proxy({
        #     'proxyType': ProxyType.MANUAL,
        #     'httpProxy': pro,
        #     'ftpProxy': pro,
        #     'sslProxy': pro,
        #     'noProxy': ''  # set this value as desired
        # })

        # return proxy

    def get_proxy_server(self, worker_name):
        offset = int(worker_name[6:])
        assert isinstance(offset, (int, long)), "worker name should be followed by integer e.g. worker1"
        return '127.0.0.1:', int(self.task_obj.myProxy["mitm_server_proxy"]) + offset

    def fetch_url(self, task_obj):
        print "Fetching : ", task_obj.url
        try:
            self.driver.get(task_obj.url)
            time.sleep(5)
            self.set_screenshot(task_obj)
        except WebDriverException:
            print "error encountered with chrome webdriver"

    def set_screenshot(self, task_obj):
        try:
            task_obj.image = self.driver.get_screenshot_as_png()
        except WebDriverException:
            print "error encountered with chrome webdriver"

    def get_visible_text(self, content):
        retval = ""
        soup = BeautifulSoup(content, 'html.parser')
        texts = soup.findAll(text=True)


        # # content = Cleaner().clean_html(content)
        # doc = fromstring(content, parser=etree.XMLParser(recover=True))
        #
        # for element in doc.iterdescendants():
        #     if element.tag not in ['script', 'noscript', 'style']:
        #         text = element.text or ''
        #         tail = element.tail or ''
        #         retval = retval + ' '.join((text, tail)).strip()

        return retval