class TaskObject(object):

	def __init__(self, producer_name, url, crawl_method, data_req, myProxy, db, tags=None):

		"""
		:param producer_name: The name of the producer that we are using
		:param url: the url we want to crawl
		:param crawl_method: the method of crawling e.g. native crawl or through selenium
		:param data_req: the data packets that should be stored from the packet e.g. javaScript, html
		:param myProxy: the proxy that we should employ
		:param db: the name of the database where we should store the collected data
		:param worker_name: the name of the worker who is executing this task_obj, at the start it will be none
							but will be updated once this task is assigned to any worker
		:param time_stamp : the time stamp at which this task started executing
		:param ip: the ip of the param url, it will be updated when the task starts executing
		:param doc_id: Document id of this task store in couchDB
		:param tag : list of tag specified for this urls
		Note : all the fields which are none here will be updated once the task starts executing
		"""
		self.producer_name = producer_name
		self.url = url
		self.crawl_method = crawl_method
		self.data_req = data_req
		self.myProxy = myProxy
		self.db = db
		self.visible_text = ''
		self.mitm_timeout = None
		self.image = None
		self.worker_name = None
		self.time_stamp = None
		self.ip = None
		self.success = True
		self.page_source = None
		self.doc_id = None
		self.tags = tags
