from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *
import time
import sys

def get_selenium_handler(browser_mod, browser_name):
    try:
        browser_mod = "seleniumhandler." + browser_mod
        browser_module = __import__(browser_mod, fromlist=browser_name)
        browser_obj = getattr(browser_module, browser_name)
        return browser_obj
    except ImportError:
        print >> sys.stderr, "browser module doesn't exist : %s" % browser_name
    except AttributeError:
        print >> sys.stderr, \
            "To instantiate, class name should be same as module name, module name is : %s"%browser_mod

