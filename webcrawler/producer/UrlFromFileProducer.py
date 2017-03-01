from TaskObject import TaskObject
from Producer import Producer
from .utils import *


class UrlFromFileProducer(Producer):

    def __init__(self, args):
        super(UrlFromFileProducer, self).__init__('UrlFromFileProducer', args.num_of_url=None)
        self.args = args
        print "Instantiating UrlFromFileProducer"

    def get_task_list(self, num_of_url=None):
        """
        :param num_of_url: from the given text file containing '\n' separated urls retrive the num_of_url
        :return: list of url

        This method assume that the file will contain the urls in separated line
        """
        print "returning list"
		task_list = list()
		url_list = open(self.args.url_file, 'r').read().splitlines()
		while url_list:
			task_list.append(get_object(url_list[0]))
			url_list = url_list[1:]
		return task_list

    def get_object(self, url):
        return TaskObject("UrlFromFileProducer",
                          "http://"+url,
                          "selenium_chrome",
                          set_data_requirement(self.args),
                          set_proxy(self.args),
                          set_db(self.args))
