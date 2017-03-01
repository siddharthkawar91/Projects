from TaskObject import TaskObject
from Producer import Producer
from .utils import *


class UrlFromDropped(Producer):

    def __init__(self, args):
        super(UrlFromDropped, self).__init__('UrlFromDropped', args.num_of_url)
        self.args = args
        print "Instantiating UrlFromDropped"

    def get_list_url(self, num_of_url=None):
        """
        :param num_of_url: from the given text file containing '\n' separated urls retrive the num_of_url
        :return: list of url

        This method assume that the file will contain the urls in separated line
        """
        print "returning list"
        lines =  open(self.args.url_file, 'r').read().splitlines()
	#removing ending dot for domains
        lines = [ [l.split(',')[0][:-1], l.split(',')[1]] for l in lines]
        return lines

    def get_object(self, url_drop):
	url, drop_date = url_drop
        return TaskObject("UrlFromFileProducer",
                          "http://"+url,
                          drop_date, 
                          "selenium_chrome",
                          set_data_requirement(self.args),
                          set_proxy(self.args),
                          set_db(self.args))
