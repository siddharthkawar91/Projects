from couchdb.mapping import Document, DictField, TextField, ListField, Mapping
from couchdb import ResourceNotFound
from Decoders.decoders import *
import sys
import couchdb


class CouchDbHandler(object):
    """
    server_conn is the url of our server example : "http://localhost:5984/"
    db_name is the name of the database at out sever
    """
    def __init__(self, server_con):
        self.couch = couchdb.Server(server_con)

    def get_db_instance(self, db_name):

        db_instance = None
        try:
            db_instance = self.couch[db_name]
        except ResourceNotFound:
            print >> sys.stderr, "there exist no database with the given name %s" % db_name
            return None
        return db_instance

    def save_document(self, db_name, doc):
        db = self.get_db_instance(db_name)
        if db:
            return doc.store(db)


class HttpPacketsDoc(Document):

        url = TextField()
	
        producer_name = TextField()
        http_transaction_list = ListField(DictField(Mapping.build(
            http_request=DictField(),
            http_response=DictField(),
        )))
        crawl_method = TextField()
        website_content = TextField()
        javascript_content = ListField(TextField())
        worker_name =  TextField()
        time_stamp = TextField()
        ip = TextField()
        success = TextField()

