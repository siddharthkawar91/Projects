from mitmproxy import controller, proxy
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.exceptions import ServerException
from Utils import *
import traceback
import sys


class MitmProxyServer(controller.Master):

	def __init__(self, server_proxy, task_obj):
	
		func_str = "mitmhandler.py __init__()"
		self.server = None
		self.task_obj = task_obj
		self.server_proxy = server_proxy
		self.create_server()
		controller.Master.__init__(self, self.server)
		self.http_transaction_list = list()
		self.javascript_content = list()

	def create_server(self):
		func_str = "mitmhandler.py create_server()"
		host, port = self.server_proxy.split(':')
		print func_str+port
		config = proxy.ProxyConfig(port=int(port),
								   cadir="~/.mitmproxy/")
		try:
			self.server = ProxyServer(config)
		except ServerException:
			print >> sys.stderr, "server already in use"

	def run(self):
		func_str = "mitmhandler.py run() :"
		try:
			controller.Master.run(self)
		except:
			print func_str+"signal received to stop mitmproxy server...shutting down"
			self.shutdown()
			try:
				store_res(self.task_obj, self.http_transaction_list,
								   self.javascript_content)
			except:
				print func_str+"document storing failed...!"
				traceback.print_exc(file=sys.stdout)
			

	def handle_request(self, f):
		f.reply()

	def handle_response(self, f):

		if "javascript" in f.response.headers.get("content-type", "identity"):
			self.javascript_content.append(f)
			
		if 'all' in self.task_obj.data_req:
			self.http_transaction_list.append(f)
		elif f.response.headers.get("content-type", "identity").split(';')[0] \
				in self.task_obj.data_req:
			self.http_transaction_list.append(f)
		f.reply()

if __name__ == "__main__":

	m = MitmProxyServer('127.0.0.1:8081')
	m.run()
