import argparse
from Tasks import *

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("name", help="name of python script of producer to run")
	parser.add_argument("--num_of_url", help="the num of URLs to be retrieved using your producer",
						type=int)
	parser.add_argument("proxy_file", help="specify the conf file for proxy")
	parser.add_argument("--url_file", help="specify the path of the url")
	args = parser.parse_args()
	producer_module = __import__('producer.'+args.name, fromlist=[''])
	
	"""
		Note that the name of the producer name should be same as the class name. 
		for e.g. 
		the class name for the AlexaProducer is "AlexaProducer". Then one should provide the same name 
		as the class name (case sensitive)
	"""
	
	"""
		currently we support two method to crawl selenium_chrome and selenium_firefox
	"""
	crawl_method = {
		"selenium_firefox": crawl_selenium,
		"selenium_chrome": crawl_selenium
	}
	
	"""
		on the basis of the name provided we take two  producer name and then create a object of that producer.
		we then use it to create a class of the same and retrieve the url list from the producer
	"""
	producer_obj = None
	try:
		producer_obj = getattr(producer_module, args.name)(args)
	except AttributeError:
		print >> sys.stderr, "producer module doesn't contains the class with producer name"
	base_dir = os.path.dirname(os.path.realpath(__file__))
	assert os.path.isfile(args.proxy_file), "files doesn't exist : " + args.proxy_file
	
	if args.url_file:
		assert os.path.isfile(args.url_file), "files doesn't exist : " + args.url_file

	if args.name == "AlexaProducer": 
		assert args.num_of_url is not 0, "num of urls cannot be zero"

	crawl_task_list = producer_obj.get_task_list(args.num_of_url)
   
	while crawl_task_list:
		"""
			crawl_task_list : the list of task that we obtained from the producer
			We are taking each task object in the task list and then putting that 
			task in the celery queue through delay() method
		"""
		task = crawl_task_list[0]
		crawl_method[task.crawl_method].delay(task)
		crawl_task_list = crawl_task_list[1:]

main()
