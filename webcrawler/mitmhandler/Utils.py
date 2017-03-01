from couchdbhandler.couchdbhandler import *
from couchdb.mapping import ListField, TextField, DictField
from Decoders.decoders import *


def store_resources(db, http_packet_doc, http_transaction_list):

	filename_prefix = "attachment"
	counter = -1
	
	for http_flow in http_transaction_list:
		if http_flow.response:
			responses = http_flow.response
			counter += 1
			assert responses is not None

			#if responses.status_code == 200 and responses.headers.get("content-length") > 0:
			#we want to dump all responses and it may not have content-length field
			if True:
				content_encoding = responses.headers.get("content-encoding", "identity")
				content_type = responses.headers.get("content-type", "identity")
				#NOTE space saving based on https://www.sitepoint.com/web-foundations/mime-types-complete-list/
				if "text/html" in content_type or "text/x-server-parsed-html" in  content_type or "text/javascript" in content_type or "application/x-javascript" in content_type or "application/javascript" in content_type or "application/ecmascript" in content_type or "text/ecmascript" in content_type:
					decompress_content = responses.content

					if content_encoding in decompress_dict:
						decompress_content = decompress_dict[content_encoding](responses.content)
						responses.content = decompress_content

					db.put_attachment(http_packet_doc, decompress_content, filename_prefix + str(counter), 
									  content_type)

def store_res(task_obj, http_transaction_list, javascript_content):
	func_str = "Utils.py store_res()"
	
	couch_handler = CouchDbHandler(task_obj.myProxy["couchdb_server_proxy"])
	db_instance = couch_handler.get_db_instance(task_obj.db)
	
	print func_str+"retrieving document..."+repr(task_obj.doc_id)
	http_packet_doc = db_instance.get(task_obj.doc_id)
	
	if http_transaction_list:	
		print func_str+"storing http_transaction_list"
		add_http_transaction_list(http_packet_doc, http_transaction_list)
		add_javascript_content(http_packet_doc, javascript_content)
	else:
		print func_str+"http_transaction_list is empty.."
	db_instance.save(http_packet_doc)
	
	store_resources(db_instance, http_packet_doc, http_transaction_list)
	
def add_http_transaction_list(doc, http_transaction_list):
	_http_transaction_list = convert_http_transaction_list(http_transaction_list)
	
	doc["http_transaction_list"] = list()
	for http_transaction in _http_transaction_list:
		app_val = dict()
		app_val["http_request"] = http_transaction[0]
		app_val["http_response"] = http_transaction[1]
		doc["http_transaction_list"].append(app_val)
		
def add_javascript_content(doc, javascript_content):
	doc["javascript_content"] = list()
	for http_flow in javascript_content:
		if http_flow.response:
			responses = http_flow.response
			assert responses is not None

			if responses.status_code == 200 :
			#if responses.status_code == 200 and responses.headers.get("content-length") > 0: some do not have content-length
				content_type = responses.headers.get("content-type", "identity")
#				if "text/javascript" in content_type or "application/x-javascript" in content_type or "application/javascript" in content_type or "application/ecmascript" in content_type or "text/ecmascript" in content_type:
				if "text/javascript" in content_type:
					content_encoding = responses.headers.get("content-encoding", "identity")
					decompress_content = responses.content

					if content_encoding in decompress_dict:
						decompress_content = decompress_dict[content_encoding](responses.content)
						responses.content = decompress_content
						try:
							doc["javascript_content"].append(decompress_content.encode('utf-8'))
						except UnicodeDecodeError as e:
							print "UnicodeDecodeError",e
							
							


def convert_http_transaction_list(http_transaction_list):

	_http_transaction_list = []
	for http_transaction in http_transaction_list:
		if http_transaction:
			transaction = []

			req = convert_http_request_to_dict(http_transaction.request)
			res = convert_http_response_to_dict(http_transaction.response)

			transaction.append(req)
			transaction.append(res)
			_http_transaction_list.append(transaction)

	return _http_transaction_list


def convert_http_request_to_dict(http_request):

	func_str="Utils.py convert_http_request_to_dict() :"
	request_dict = dict()
	request_dict['url'] = http_request.url.encode('utf-8')
	for field in http_request.headers.fields:
		if isinstance(field[1], str):
			try:
				request_dict[field[0].lower()] = field[1].encode('utf-8')
			except UnicodeDecodeError as e:
				print func_str + "UnicodeDecodeError",e
		else:
			request_dict[field[0].lower()] = field[1]
	return request_dict


def convert_http_response_to_dict(http_response):

	func_str="Utils.py convert_http_response_to_dict() :"
	response_dict = dict()
	response_dict['status'] = http_response.status_code
	for field in http_response.headers.fields:
		if isinstance(field[1], str):
			try:
				response_dict[field[0].lower()] = field[1].encode('utf-8')
			except UnicodeDecodeError as e:
				print func_str+"UnicodeDecodeError",e
		else:
			response_dict[field[0].lower()] = field[1]

	return response_dict
