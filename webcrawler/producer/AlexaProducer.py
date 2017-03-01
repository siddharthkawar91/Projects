from lxml import html
import requests
from TaskObject import TaskObject
from Producer import Producer
from .utils import *


class AlexaProducer(Producer):

	def __init__(self, args):
		super(AlexaProducer, self).__init__('http://www.alexa.com/topsites', args.num_of_url)
		self.args = args
		print "Instantiating AlexaProducer"
		
	def get_list_url(self, num_of_url):
		"""
			This is the get_list_url method every class should provide the get_list_url method.
		"""
		init_crawling_list = []
		print "Fetching %s URL from Alexa ..." % num_of_url
		run_cond = True
		counter_url = 0
		append_url = "/global;"
		fetch_url = self.website_url + append_url + str(counter_url)
		counter = 0

		while run_cond:
			page = requests.get(fetch_url)
			tree = html.fromstring(page.content)
			url_list = tree.xpath('//a[starts-with(@href, "/siteinfo/")]/@href')

			for i in url_list:
				i = i[10:]
				if i != "" and counter < num_of_url:
					i = "http://www." + i
					init_crawling_list = init_crawling_list + [i]
					counter += 1
				elif counter >= num_of_url:
					run_cond = False
					break
			if counter >= num_of_url:
				break
			counter_url += 1
			fetch_url = self.website_url + append_url + str(counter_url)

		return init_crawling_list

	def get_object(self, url):
		"""
			we are returning here TaskObject instance. This instance contains all the parameters
			which will then decide how to crawl the task. Every producer class should provide the 
			implementation of the get_object method.
		"""
		return TaskObject("Alexa Producer",
						  url,
						  "selenium_chrome",
						  set_data_requirement(self.args),
						  set_proxy(self.args),
						  set_db(self.args))

