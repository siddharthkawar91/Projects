#!/bin/bash
fuser -k 10001/tcp
fuser -k 10002/tcp
fuser -k 10003/tcp
fuser -k 10004/tcp
fuser -k 10005/tcp
fuser -k 10006/tcp
fuser -k 10007/tcp
fuser -k 10008/tcp
fuser -k 10009/tcp
fuser -k 10010/tcp
fuser -k 10011/tcp
fuser -k 10012/tcp
fuser -k 10013/tcp
fuser -k 10014/tcp
fuser -k 10015/tcp
fuser -k 10016/tcp
fuser -k 10017/tcp
fuser -k 10018/tcp
fuser -k 10019/tcp
fuser -k 10020/tcp
celery -f -A Tasks purge
ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
