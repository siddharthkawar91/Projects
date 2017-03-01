from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class SeleniumTest(object):

    def __init__(self, url):
        PROXY = '127.0.0.1:8086'
        # proxy = Proxy({
        #     'proxyType': ProxyType.MANUAL,
        #     'httpProxy': PROXY,
        #     'ftpProxy': PROXY,
        #     'sslProxy': PROXY,
        #     'noProxy': None
        # })
        # webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        #     "httpProxy": PROXY,
        #     "ftpProxy": PROXY,
        #     "sslProxy": PROXY,
        #     "noProxy": None,
        #     "proxyType": "MANUAL",
        #     "class": "org.openqa.selenium.Proxy",
        #     "autodetect": False
        #
        # }
        # webdriver.DesiredCapabilities.FIREFOX['binary'] = '/usr/bin/firefox'
        # webdriver.DesiredCapabilities.FIREFOX['timeout'] = 150

        # d = webdriver.Remote("http://127.0.0.1:4444/wd/hub", webdriver.DesiredCapabilities.FIREFOX)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", "127.0.0.1")
        profile.set_preference("network.proxy.http_port", int(8081))
        profile.update_preferences()
        d = webdriver.Firefox(firefox_profile=profile)
        d.get(url)

        try:
            WebDriverWait(d, 3).until(EC.alert_is_present(),
                                            'Timed out waiting for PA creation ' +
                                            'confirmation popup to appear.')

            alert = d.switch_to.alert.text
            time.sleep(2)
            print alert
            print "alert accepted"
        except TimeoutException:
            print "no alert"

    def set_firefox_proxy(self):

        pro = "127.0.0.1:8081"
        print "Firefox : ", pro
        proxy = Proxy({
            "proxyType": ProxyType.MANUAL,
            "httpProxy": pro,
            "ftpProxy": pro,
            "sslProxy": pro,
            "noProxy": ''  # set this value as desired
        })
        return proxy

SeleniumTest("http://www.google.com")
