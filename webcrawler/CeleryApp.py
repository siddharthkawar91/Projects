from celery import Celery

app = Celery('WebCrawlerV1',
             broker='amqp://guest:crawler1%40@130.245.32.55:5672',
             backend='amqp://',
			 soft_time_limit=60,
             include=['Tasks'])

# 'broker' indicates the address of the rabbitmq server. you can specify this in the proxy1.ini file
# 'include' indicates the file name of the tasks which this celery application will execute.
# 'backend' indicates where you want to store the result. We are currently not using this we store our result in couchdb 
# 'soft_time_limit' indicates the time out limit for the task to get finished it allows gracious exits of the task.