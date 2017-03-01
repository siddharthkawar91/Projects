from TaskObject import TaskObject
from Producer import Producer
from .utils import *


class TagProducer(Producer):

	def __init__(self, args):
		super(TagProducer, self).__init__('TagProducer', args.num_of_url)
		self.args = args
		print "Instantiating TagProducer"
		
	def get_task_list(self, num_of_url=None):
		"""
		:param num_of_url: from the given text file containing '\n' separated urls retrive the num_of_url
		:return: Dict with type as key and urls as values example :-
			d['bank-sites'] = {"www.wellsfargo.com", "www.icici.com"}

		This method assume that the file will contain the urls in separated line
		"""
		
		url_list = open(self.args.url_file, 'r').read().splitlines()
		print url_list
		task_list= list()
		curr_tags = None
		while url_list:
			url = url_list[0]
			if url is "":
				url_list = url_list[1:]
				continue
			if "[" in url:
				url = url[1:-1]
				curr_tags = url.split(",")
			else:
				if curr_tags:
					print str(curr_tags)
					task_list.append(self.get_object(url, curr_tags))
				else:
					print >> sys.stderr, "specified url file not in proper format..list of tags missing..!!"
					return None
			url_list = url_list[1:]
		return task_list
		
	def get_object(self, url, tags):
		return TaskObject("TagProducer",
						  "http://"+url,
						  "selenium_chrome",
						  set_data_requirement(self.args),
						  set_proxy(self.args),
						  set_db(self.args), 
						  tags)
