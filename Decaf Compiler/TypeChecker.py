from AST import *
import sys


class TypeChecker(object):

    def __init__(self,class_table):
        self.class_table = class_table
        self.subtypetuple = {"int" : ["int","float"], "float" : ["float"],"null" :["null"],"boolean" : ["boolean"],"void" : ["void"],"string":["string"]} #int is subtype of int and float
        class_table.subtypetuple = self.subtypetuple
        self.inflateSubTypeRelation()
        #self.printSubTypeRelation()
        self.error = False
        self.TypeCheck()
        self.retfound = False
#         if(self.error == False):
#               self.class_table.PRINT()

    def inflateSubTypeRelation(self):
        for CLASS in self.class_table.children :
            if CLASS.super_name is "":
                self.subtypetuple["null"] = self.subtypetuple["null"] + [CLASS.name]
                self.subtypetuple[CLASS.name] = [CLASS.name]  #class.name is subtype of class.supername
            else:
                if CLASS.super_name not in self.subtypetuple:
                    print >> sys.stderr, "error : %s definition not found" %(CLASS.super_name)
                else :
                    self.subtypetuple["null"] = self.subtypetuple["null"] + [CLASS.name]
                    self.subtypetuple[CLASS.name] = [CLASS.name] + self.subtypetuple[CLASS.super_name]

    def printSubTypeRelation(self):
        print self.subtypetuple

    def TypeCheck(self):
        for CLASS in self.class_table.children :
            if(CLASS.name == "In" or CLASS.name == "Out"):
                continue
            for Method in CLASS.Methods:
                for Method_new in CLASS.Methods:
                    if (Method==Method_new or Method.name!=Method_new.name):
                        continue
                    else:
                        if(self.issubtype(self.gettype_of_METHOD(Method.param),self.gettype_of_METHOD(Method_new.param),self.class_table) and self.issubtype(self.gettype_of_METHOD(Method_new.param),self.gettype_of_METHOD(Method.param),self.class_table)):
                            print >> sys.stderr, "error : Identical Methods defined at line %d and line %d "%(Method.lineno[0],Method_new.lineno[0])
                            sys.exit()
                            
                if(Method.body is not None):
                   if(Method.body.RESOLVE(CLASS,self.class_table)=="error"):
                       self.error = True
                if(self.CheckRtype(Method)=="error"):
                    self.error = True

            for Constructor in CLASS.CConstructors :
                for Constructor_new in CLASS.CConstructors:
                    if (Constructor==Constructor_new):
                        continue
                    else:
                        if(self.issubtype(self.gettype_of_METHOD(Constructor.param),self.gettype_of_METHOD(Constructor_new.param),self.class_table) and self.issubtype(self.gettype_of_METHOD(Constructor_new.param),self.gettype_of_METHOD(Constructor.param),self.class_table)):
                            print >> sys.stderr, "error : Identical Constructors defined at line %d and line %d "%(Constructor.lineno[0],Constructor_new.lineno[0])
                            sys.exit()
                            
                if(Constructor.body is not None):
                    if(Constructor.body.RESOLVE(CLASS,self.class_table)=="error"):
                        self.error = True
                if(self.CheckRtype(Constructor)=="error"):
                    self.error = True

    def CheckRtype(self,element):
        if element.type == "METHOD":
            self.retfound = False

            if element.body is not None and element.body != []:
                for y in element.body.body:
                    if y.type == "stmt":
                        if( not self.CheckStmt(y,element.rtype)):
                             return "error"

                if(not self.retfound and element.rtype != "void"):
                    print >> sys.stderr,"error : return statement missing for method %s at lineno %d" %(element.name,element.lineno[0])
                    return "error"
            else:
                if(element.rtype != "void"):        #Body is None and rtype of method is not void then error
                    print >> sys.stderr,"error : return statement missing in method %s at lineno %d : " %(element.name,element.lineno[0])

        elif element.type == "CONSTRUCTOR":
            rtype = None
            if element.body is not None:
                for y in element.body.body:
                    if y.type == "stmt" and y.stmtType == "Return":

                        print >> sys.stderr,"error : unexpected return type at lineno %d"%(y.lineno[0])
                        return "error"

    def CheckStmt(self,stmt,rtype):
        if isinstance(stmt, Expression):
            return True

        if stmt.stmtType == "Return":
            self.retfound = True
            if(self.Determine_type_relation(rtype,stmt.exp_rtype,self.class_table) ==3 or self.Determine_type_relation(rtype,stmt.exp_rtype,self.class_table) ==1):
                return True
            else:
                print >> sys.stderr, "error : incompatible type : %s cannot be converted to %s at lineno %d" %(stmt.exp_rtype,rtype,stmt.lineno[0])
                return False

        elif stmt.stmtType == "If":
            if stmt.elseStmt:
                return self.CheckStmt(stmt.thenStmt,rtype) and self.CheckStmt(stmt.elseStmt,rtype)
            else:
                return self.CheckStmt(stmt.thenStmt,rtype)

        elif stmt.stmtType == "While":
            return self.CheckStmt(stmt.loopBody,rtype)

        elif stmt.stmtType == "For":
            return self.CheckStmt(stmt.loopBody,rtype)

        elif stmt.stmtType == "Block":
           if stmt.body is not None:
                bool = True
                for y in stmt.body:
                    if y.type == "stmt":
                        bool = bool and self.CheckStmt(y,rtype)
                return bool
           else:
               return True
        else:
            return True

    def Determine_type_relation(self,rtype1,rtype2,AST_TABLE):
        if(rtype1 == "error"): return -1
        if(rtype2 == "error"): return -1
        t1 = self.Extracttype(rtype1)
        t2 = self.Extracttype(rtype2)

        if(t1 == None and t2 !=None):
            if(t1 == "null"):
                return 2
            else:
                return -1
        elif(t1 !=None and t2 ==None):
            if(t2 == "null"):
                return 1
            else:
                return -1
        elif (t1 != None and t2 != None):
            return self.Determine_type_relation(t1,t2,AST_TABLE)
        else:
            if(rtype1 in AST_TABLE.subtypetuple[rtype2] and rtype2 in AST_TABLE.subtypetuple[rtype1]):
                return 3
            if (rtype1 in AST_TABLE.subtypetuple[rtype2]): return 1     #t2 is subtype of t1
            elif (rtype2 in AST_TABLE.subtypetuple[rtype1]): return 2   #t1 is subtype of t2
            else : return -1

    def gettype_of_METHOD(self,list):
        type_of_args = []                   #This list will contain the type of all parameter of method
        if (list is not None):
            for x in list:
                type_of_args = type_of_args + [x.typev]
        return type_of_args
    
    def issubtype(self,t1,t2,AST_TABLE): #check if t1 is subtype of t2

        if((t1 == []) and (t2 != [])):
            return False
        if((t1 != []) and (t2 == [])):
            return False
        if(t1 == [] and t2 == []):
            return True
        if(len(t1)!=len(t2)) :
            return False

        if( self.Determine_type_relation(t1[0],t2[0],AST_TABLE)==3 or self.Determine_type_relation(t1[0],t2[0],AST_TABLE)==2):
            t1_tail = t1[1:]
            t2_tail = t2[1:]
            return True and self.issubtype(t1_tail,t2_tail,AST_TABLE)
        
    def Extracttype(self,rtype):
        if(rtype[:6] == "array("):
            rtype = rtype[6:-1]
            return rtype
        elif(rtype[:5] == "User("):
            rtype = rtype[5:-1]
            return rtype
        elif(rtype[:14] == "class-literal("):
            rtype = rtype[14:-1]
            return rtype
        else:
            return None
