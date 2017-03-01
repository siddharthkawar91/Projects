

class Producer(object):

    def __init__(self, website_url=None, no_of_urls=None):
        self.no_of_URLs = no_of_urls
        self.website_url = website_url

    def print_crawling_list(self, retrieved_list):
        print "Top URLs from %s : " % self.website_url
        for url_iter in retrieved_list:
            print url_iter
