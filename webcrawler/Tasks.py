from TaskObject import *
from lxml import html
from CeleryApp import app
from mitmhandler.mitmhandler import *
from threading import Thread
from seleniumhandler.selenium_handler import *
from seleniumhandler import *
from couchdbhandler.couchdbhandler import *
from utils import *
from time import strftime
from billiard import current_process
from billiard import Process
from billiard import Manager
from celery.exceptions import SoftTimeLimitExceeded
from datetime import datetime
import requests
import signal
import psutil
import os
import sys
import traceback
import socket

SOFT_TIME_LIMIT = 60
MITM_TIMEOUT = 40

browser_to_module = {
	"selenium_chrome": "SeleniumChrome",
	"selenium_firefox": "SeleniumFirefox"
}

def print_info(task_obj):
   print "Fetching : ", task_obj.url


def get_worker_name(p):

	"""worker string e.g. celery23@worker1.%h"""
	print "worker name : " + p.initargs[1]
	print p.initargs[1].split('@')[0]
	return p.initargs[1].split('@')[0]
	#return (p.initargs[1].split('@')[1]).split('.')[0]


def kill_child(pid):
	parent = psutil.Process(pid)
	for child in parent.children(recursive=True):
		try:
			child.kill()
		except psutil.NoSuchProcess:
			pass

def start_proxy(worker_name, task_obj):

	server_name = get_proxy_server(worker_name, task_obj.myProxy["mitm_server_proxy"])
	m = MitmProxyServer(server_name, task_obj)
	m.run()
	return

def get_proxy_server(worker_name, mitm_proxy_port):
	offset = int(worker_name[6:])
	assert isinstance(offset, (int, long)), "worker name should be followed by integer e.g. worker1"
	return '127.0.0.1:' + str(int(mitm_proxy_port)+offset)

def hostname_resolves(hostname):
	print "trying to resolve hostname : "
	if "http://" in hostname:
		hostname = hostname[7:]
	print hostname
	try:
		t = socket.gethostbyname(hostname)
		if t is not '':
			return t
		return ''
	except Exception:
		return ''


#@app.task(bind=True,,ignore_result=True)
@app.task(bind=True,soft_time_limit=SOFT_TIME_LIMIT, ignore_result=True)
def crawl_selenium(self, task_obj):
	func_str = "Tasks.py crawl_selenium() : "
	doc_id = None
	db = None
	p = None
	ret_val = None

	"""
		We first create an empty document
	"""
	print func_str+"creating an empty document coucbdb"
	couch_handler = CouchDbHandler(task_obj.myProxy["couchdb_server_proxy"])
	db_instance = couch_handler.get_db_instance(task_obj.db)

	try:
		ret_val = None
		hostname = hostname_resolves(task_obj.url)
		if hostname is '':
			print func_str+"hostname resolution failed for : ",task_obj.url
			print func_str+"Task completed successfully at %s!!" % strftime("%H:%M:%S")
			http_packet_doc = HttpPacketsDoc(url=task_obj.url,
									 producer_name=task_obj.producer_name,
									 crawl_method=task_obj.crawl_method,
									 worker_name=current_process().initargs[1],
									 ip=hostname,
									 time_stamp=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
			if db_instance:
				http_packet_doc.store(db_instance)
			else:
				print func_str+"db_instance is null"
			return
		try:
			"""
			start the mitmproxy server in the separate process
			launcing browser instance to fetch url
			Terminating the process of mitmproxy server
			"""
			print_info(task_obj)
			worker_name = get_worker_name(current_process())
			task_obj.worker_name = current_process().initargs[1]
			task_obj.ip = hostname
			task_obj.time_stamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

			http_packet_doc = HttpPacketsDoc(url=task_obj.url,
									 producer_name=task_obj.producer_name,
									 crawl_method=task_obj.crawl_method,
									 worker_name=current_process().initargs[1],
									 ip=hostname,
									 time_stamp=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))

			http_packet_doc.store(db_instance)
			task_obj.doc_id = http_packet_doc.id

			""" cleaning up any unkilled child"""
			kill_child(os.getpid())


			print func_str+"starting mitmproxy server"
			p = Process(target=start_proxy,
						args=(worker_name, task_obj))
			p.start()

			try:
				print func_str+"starting selenium handler"
				get_selenium_handler(task_obj.crawl_method,
									 browser_to_module[task_obj.crawl_method])(task_obj, worker_name)
			except:
				print func_str+"get_selenium_handler failed..!"
				traceback.print_exc(file=sys.stdout)
			print func_str+"sending signal ... to kill mitmproxy server"

			p.terminate()

			if not p.is_alive():
				print func_str+"mitm proxy server halted"
			else:
				print func_str+"mitm proxy server saving data to couchdb"
			p.join(MITM_TIMEOUT)

			if p.is_alive():
				print func_str+"mitmproxy is alive even after p.join()......forceful termination"
				p.terminate()

			print func_str+"terminated mitmproxy server"
			doc_id = task_obj.doc_id

			if doc_id:

				db = db_instance
				if db:
					doc = db.get(doc_id)
					doc["website_content"] = task_obj.visible_text
					doc["success"] = "True"
					doc["page_source"] = task_obj.page_source
					print "adding tags " + str(task_obj.tags)
					if task_obj.tags:
						print "adding tags.."
						doc["tags"] = task_obj.tags
					db.save(doc)

					if task_obj.image:
						print func_str+"saving screenshot"
						db.put_attachment(doc , task_obj.image, "screenshot", "image/png")
					else:
						print func_str+"there is no screenshot to store"

				else:
					print func_str + "db instance is null...no database"
			else:
				print func_str+"mitmproxy server returned process returned no doc_id"
			kill_child(os.getpid())

			print "Task completed successfully at %s!!" % strftime("%H:%M:%S")
		except Exception as e:
			print "Global Exception " + func_str+" ",e

			traceback.print_exc(file=sys.stdout)

			if p and p.is_alive():
				p.terminate()
				p.join(20)
				p.terminate()

			doc_id = task_obj.doc_id
			if doc_id:
				print func_str+"doc_id found...storing data after failure reported"
				db = db_instance
				doc = db.get(doc_id)
				doc["url"] = task_obj.url
				doc["ip"] = task_obj.ip
				doc["success"] = "False"
				db.save(doc)
			else:
				print func_str+"no document id found...."
			kill_child(os.getpid())


	except SoftTimeLimitExceeded as e:
		print func_str+"exception occured : "
		if p.is_alive():
			p.terminate()
			p.join(20)
			p.terminate()
		kill_child(os.getpid())

@app.task
def crawl_native_python(task_obj):
	pass
#
#         mitm_server = MitmProxyServer(task_obj.myProxy["mitm_server_proxy"])
#
#         def call_stop_mitm_proxy(num, stack):
#             mitm_server.shutdown()
#
#         url_list = []
#         t = Thread(target=start_mitm_proxy, args=(mitm_server, ))
#         t.start()
#         signal.signal(signal.SIGINT, call_stop_mitm_proxy)
#         page = requests.get(task_obj.url, timeout=7, proxies=task_obj.myProxy["native_proxy"],
#                             verify='/home/siddharth/.mitmproxy/mitmproxy-ca-cert.pem')
#
#         os.kill(os.getpid(), signal.SIGINT)
#         tree = html.fromstring(page.content)
#         url_list = url_list + tree.xpath('//a[starts-with(@href, "http")]/@href')
#         print "Connecting to CouchDB..."
#         print "Storing Doc..."
#         http_packet_doc = HttpPacketsDoc(url=task_obj.url, producer_name=task_obj.producer_name,
#                                          crawl_method=task_obj.crawl_method)
#
#         http_packet_doc.add_http_transaction_list(mitm_server.http_transaction_list)
#         store_doc(task_obj, http_packet_doc, mitm_server)
#         print "Task completed successfully at %s!!" % strftime("%H:%M:%S")
#         return url_list
