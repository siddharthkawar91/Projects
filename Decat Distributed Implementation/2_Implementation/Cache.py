from datetime import datetime

class TentativeSubjectUpdatesCache:
    def __init__(self):
        self.cache = dict()

    def add(self, request):
        key = request['subjectId']
        value = {
            'requestId' : request['requestId'],
            'attributes' : request['attributeUpdates']['subject'],
            'timestamp' : datetime.now()
        }
        self.cache[key] = value
        return value

    def get(self, subjectId):
        if subjectId in self.cache:
            return self.cache[subjectId]
        else:
            return None

    def remove(self, subjectId):
        if subjectId in self.cache:
            del self.cache[subjectId]
            return True
        else:
            return False

class SubjectCache:
    def __init__(self):
        self.cache = dict()

    def add(self, request):
        key = request['subjectId']
        value = {
            'attributes' : request['attributeUpdates']['subject'],
            'timestamp' : datetime.now()
        }
        self.cache[key] = value
        return value

    def get(self, subjectId):
        if subjectId in self.cache:
            return self.cache[subjectId]
        else:
            return None

    def remove(self, subjectId):
        if subjectId in self.cache:
            del self.cache[subjectId]
            return True
        else:
            return False


class ResourceCache:
    def __init__(self):
        self.cache = dict()

    def add(self, request):
        key = request['resourceId']
        value = {
            'attributes' : request['attributeUpdates']['resource'],
            'timestamp' : datetime.now()
        }
        self.cache[key] = value
        return value

    def get(self, resourceId):
        if resourceId in self.cache:
            return self.cache[resourceId]
        else:
            return None

    def remove(self, resourceId):
        if resourceId in self.cache:
            del self.cache[resourceId]
            return True
        else:
            return False