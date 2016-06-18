import sys
from fileinput import filename

class Stack(object):

    def __init__(self,list):
        self.list = list

    #return true or false
    def isEmpty(self):
        return not self.list

    #Push function to push the data in stack
    def Push(self,data):
        self.list.append(data)

    def Pop(self):
        if self.isEmpty():
            print "stack : empty"
            sys.exit(-1)
        return self.list.pop()

    def Top(self):
        if self.isEmpty():
            print "stack : empty"
            sys.exit(-1)
        return self.list[len(self.list)-1]


class Abstract_Regsiter_Machine(object):

    def __init__(self,fileName):
        self.f = open(fileName.split(".")[0]+".ami",'w')
        self.register = 0
        self.label = 0
        self.arg = 0
        self.fregister = 0

    def Generate_new_temporary(self):

        loc = "t"+str(self.register)
        self.register = self.register + 1
        return loc

    def Generate_new_floating_temporary(self):
        loc = "f"+str(self.fregister)
        self.fregister = self.fregister + 1
        return loc

    def Generate_new_label(self):

        label = "L"+str(self.label)
        self.label = self.label + 1
        return label

    def alloc_argument_register(self):
        loc = "a"+str(self.arg)
        self.arg = self.arg + 1
        return loc
    
    def write(self,mcode):
        self.f.write(mcode)

