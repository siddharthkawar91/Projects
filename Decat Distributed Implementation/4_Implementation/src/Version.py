class Version(object):
    def __init__(self, rts, wts, val):
        self.rts = rts
        self.wts = wts
        self.pendMightRead = []
        self.val = val
    def __repr__(self):
        return " Version.rts = " +str(self.rts)+" Version.wts = "+str(self.wts) \
         + " Version.pendMightRead = " + str(self.pendMightRead) +" Version.val = " + str(self.val)  

class DBVersion(object):
    def __init__(self, ts, val):
        self.ts = ts
        self.val = val