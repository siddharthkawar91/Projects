from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from lxml.html.clean import Cleaner
from lxml.html import fromstring
import os
import time
import traceback
import sys
import fcntl
import psutil



PAGE_LOAD_TIMEOUT = 35

class SeleniumChrome(object):

	def __init__(self, task_obj, worker_name):
		self.display = None
		self.driver = None
		self.PIDs = None
		func_str = "selenium_chrome.py __init__() :"
		while True:
			try:
				with open('/tmp/xvfb.lock','w') as lock:

					fcntl.lockf(lock, fcntl.LOCK_EX)
					self.display = Display(visible=0, size=(1024, 768))
					fcntl.lockf(lock, fcntl.LOCK_UN)

					self.display.start()
					self.task_obj = task_obj
					self.browser_name = "chrome"
										#driver_path =os.path.join( os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'chromedriver'+str(int(worker_name[6:])%10))
#					self.driver = webdriver.Chrome('/home/consumervm/webcrawler/WebCrawlerV1/chromedriver'+str(int(worker_name[6:])%10),
					self.driver = webdriver.Chrome(chrome_options=self.set_chrome_opt(worker_name))
					try:
						self.PIDs = psutil.Process(self.driver.service.process.pid).children(recursive=True)
						print "chrome PID : " + str(self.PIDs)
					except:
						print func_str+ " failed to get chrome PID."
						self.PIDs = None
					self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
					print func_str+"going to fetch url"
					try:
						self.fetch_url(task_obj)
					except TimeoutException:
						print func_str+"time out occurred"

					visible_text = self.driver.page_source
					self.task_obj.page_source = visible_text
					self.task_obj.visible_text = self.get_visible_text(visible_text)

					self.driver.quit()
					self.display.stop()
					if self.PIDs:
						for p in self.PIDs:
							try:
								p.kill()
								print "success in killing PID: " + str(p)
							except Exception as e :
								print func_str+"exception in killing chrome processes" + str(e)
					print func_str+"exiting __init__"
					break
			except Exception as e:
				print func_str+"exception occured ",e
				if self.driver:
					visible_text = self.driver.page_source
					self.task_obj.page_source = visible_text
					self.task_obj.visible_text = self.get_visible_text(visible_text)
					self.driver.quit()
				else:
					print func_str+"dirver object is None cannot save page_source"
				if self.display:
					self.display.stop()
				if self.PIDs:
					for p in self.PIDs:
						try:
							p.kill()
							print "success in killing PID: " + str(p)
						except Exception as e:
							print func_str+"exception in killing chrome processes" + str(e)

				break


	def get_proxy_server(self, worker_name):
		offset = int(worker_name[6:])
		assert isinstance(offset, (int, long)), "worker name should be followed by integer e.g. worker1"
		return '--proxy-server=127.0.0.1:' + str(int(self.task_obj.myProxy["mitm_server_proxy"]) + offset)

	def set_chrome_opt(self, worker_name):

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument(self.get_proxy_server(worker_name))
		chrome_options.add_argument("user-agent=Mozilla/5.0 Windows NT 5.1 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
		extension_path = os.path.join(os.path.dirname(__file__), 'injection_chrome_extension.crx')
		chrome_options.add_extension(extension_path)
		chrome_options.add_argument('--ignore-certificate-errors')
		chrome_options.binary_location = "/usr/bin/google-chrome-stable"
		return chrome_options

	def fetch_url(self, task_obj):
		func_str="selenium_chrome.py fetch_url()"
		try:
			self.driver.get(task_obj.url)
			time.sleep(5)
			self.set_screenshot(task_obj)
		except WebDriverException:
			task_obj.success = False
			traceback.print_exc(file=sys.stdout)
			print func_str+"error encountered with chrome webdriver"

	def set_screenshot(self, task_obj):
		func_str="selenium_chrome set_screenshot()"
		try:
			task_obj.image = self.driver.get_screenshot_as_png()
		except WebDriverException:
			traceback.print_exc(file=sys.stdout)
			print func_str+"error encountered with chrome webdriver while taking screenshot"

	def get_visible_text(self, content):
		func_str = "selenium_chrome.py get_visible_text()"
		retval = ""
		content = Cleaner().clean_html(content)
		doc = fromstring(content)
		#print agent in the logs
		try:
			js_res = self.driver.execute_script("return window.navigator.userAgent;")
			print func_str + 'JS User Agent: ' + js_res
			js_res = self.driver.execute_script("return window.navigator.appVersion;")
			print func_str + 'JS appVersion: ' + js_res
			js_res = self.driver.execute_script("return window.navigator.platform;")
			print func_str + 'JS platform: ' + js_res
			js_res = self.driver.execute_script("return window.navigator.oscpu;")
			print func_str + 'JS oscpu: ' + js_res

		except Exception as e:
			print func_str + 'JS exception occured: ', e

		for element in doc.iterdescendants():
			if element.tag not in ['script', 'noscript', 'style']:
				text = element.text or ''
				tail = element.tail or ''
				retval = retval + ' '.join((text, tail)).strip()

		return retval
