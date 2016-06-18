import sys
import itertools


# Generic Node definition for AST.
class Node(object):
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf


# 'CLASS_TABLE' will hold the information of all the class in the program
class CLASS_TABLE(Node):
    def __init__(self, type, children=None, leaf=None):
        self.subtypetuple = {}
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    def Insert(self, k):
        self.children.append(k)

    def PRINT(self):
        if self.children is None:
            print "CLASS TABLE is empty"
        else:
            for x in self.children:
                x.PRINT()

    def Lookup(self, key):
        for k in self.children:
            if k.name == key:
                return True
        return False

    def GetClassRef(self,key):
        for k in self.children:
            if k.name == key:
                return k


# 'ClASS' class will hold the information of the class

class CLASS(Node):
    def __init__(self, name, super_name, body):
        self.type = "CLASS"
        self.name = name
        self.super_name = super_name
        self.body = body             # this body contains the mix list of constructors,methods,fields
        self.CConstructors = []      # this contains the list of all the constructors object
        self.Methods = []            # this contains the list of all the methods object
        self.Fields = []             # this contains the list of all the fields object
        self.ExtractFromClassBody()  # This method will populate the constructor,method and field list
               # This is the offset of the class

    #body contains the list of methods,field and constructors,Below method
    #will populate the lists of methods,fields and constructors
    def ExtractFromClassBody(self):
        for x in self.body:
            for y in x:
                if isinstance(y, FIELD):
                    y.conClass = self.name
                    if (self.Field_lookup(y) == False):
                        self.Fields.append(y)
                    else:
                        print >> sys.stderr, "error : redeclaration of field %s  at line no %d" % (y.name,y.lineno[0])
                        sys.exit()
                if isinstance(y, CONSTRUCTOR):
                   if(y.name == self.name):
                        self.CConstructors.append(y)
                   else:
                        print >> sys.stderr, "error : %s defined at line no %d is neither constructor nor a method" % (y.name,y.lineno[0])
                        sys.exit()
                if isinstance(y, METHOD):
                    y.conClass = self.name
                    self.Methods.append(y)

    # Check whether the field is defined previously or not
    def Field_lookup(self, key):
        for field in self.Fields:
            if (field.name == key.name):
                return True
        return False
    # This method prints the class
    def PRINT(self):
        print "-------------------------------------------------------------------------"
        print "Class Name:", self.name
        print "Superclass Name:", self.super_name
        print "Fields: "
        for x in self.Fields:
            x.PRINT()
        print "Constructors:"
        for x in self.CConstructors:
            x.PRINT()
        print "Methods:"
        for x in self.Methods:
            x.PRINT()

    def Perform_Operation(self,generator):
        return generator.generate_CLASS(self)

class CONSTRUCTOR(Node):
    identifier = itertools.count(1).next       #This gives the unique id to the constructor

    def __init__(self, name, vis, param, block,lineno):
        self.type = "CONSTRUCTOR"
        self.name = name                    #constructor name. Need to maintain inorder to differentiate
                                            #between constructor and method
        self.id = CONSTRUCTOR.identifier()
        self.vis = vis                      #Visibility of the constructor
        self.param = param                  #Parameters of the constructor
        self.varDict = {}                   #Vartable
        self.body = block                   #Body of the Constructor
        self.lineno = lineno                #Lineno of constructor.
        self.BODYCONTAINSBLOCK(block)

    def PRINT(self):

        print "CONSTRUCTOR: %d, %s " % (self.id, self.vis)
        sys.stdout.write("Constructor Parameters: ")
        self.PRINTPARAM()
        print ""
        print "Variable Table: "
        for y in self.varDict:
            self.varDict[y].PRINT()
        print "Constructor Body: "
        self.body.PRINT()
        print ""

    def PRINTPARAM(self):
        flag = 0
        for y in self.param:
            if(flag==1):
                sys.stdout.write(",")
            flag=1
            sys.stdout.write(str(y.id))

    def BODYCONTAINSBLOCK(self,root):
        if root.body is not None:
            leaf = True           #To check if it is the leaf or not
            for y in root.body:
                if isinstance(y, BLOCK_STMT):
                    self.BODYCONTAINSBLOCK(y)
                    leaf = False
            if(leaf == True):     # This indicates the given block is the deepest block
                                  # From the deepest block we can see entire outer variables
                for m in root.var:
                    if m.id not in self.varDict:
                        self.varDict[m.id] = m

    def Perform_Operation(self,generator):
        return generator.generate_CONSTRUCTOR(self)

class METHOD(Node):
    identifier = itertools.count(1).next        #This gives unique id to the every method

    def __init__(self, name, MODLIST, param, block, rtype,lineno):
        self.id = METHOD.identifier()
        self.type = "METHOD"
        self.name = name                        # name of method
        self.vis = ""                           # Visibility of method
        self.app = ""                           # Applicability of method
        self.param = param                      # Parameter of method
        self.body = block
        self.varDict = {}
        self.lineno = lineno

        if(rtype is not None):
            self.rtype = rtype                      # Return type of method.It can be none because built in classes return nothing
        self.conClass = ""                      # Containing class of method
        self.ExtractFromModifier(MODLIST)       # Method to extract vis from MODLIST
        if(block is not None):                  # Built in class has No block.
            self.BODYCONTAINSBLOCK(block)

    def ExtractFromModifier(self, Modlist):

        if Modlist is not None:
            lenModList = len(Modlist)
        else:
            lenModList = 0

        visible = ""  # Visibility
        app = ""      # applicability

        if (lenModList == 0):
            visible = "private"
            app     = "instance"

        elif (lenModList == 1):  # if the length of modifier is One then it contains either static
            if (Modlist[0] == "static"):
                visible = "private"
                app     = "static"
            else:
                visible = Modlist[0]
                app     = "instance"
        else:
            visible = Modlist[0]
            app     = "static"


        self.vis = visible
        self.app = app

    def PRINT(self):

        print "METHOD: %d, %s, %s, %s, %s, %s" % (self.id, self.name, self.conClass,
                                                  self.vis,self.app,  self.rtype)
        sys.stdout.write("Method Parameters: ")
        self.PRINTPARAM()
        sys.stdout.write("\n")
        print "Variable Table:"
        for y in self.varDict:
            self.varDict[y].PRINT()
        print "Method Body:"
        if (self.body is not None):
            self.body.PRINT()
        print ""

    def PRINTPARAM(self):
        flag = 0
        for y in self.param:
            if(flag==1):
                sys.stdout.write(",")
            flag=1
            sys.stdout.write(str(y.id))

    def BODYCONTAINSBLOCK(self,root):
        if root.body is not None:
            leaf = True           #To check if it is the leaf or not
            for y in root.body:
                if isinstance(y, BLOCK_STMT):
                    self.BODYCONTAINSBLOCK(y)
                    leaf = False
            if(leaf == True):      #This indicates we are in the deepest block
                for m in root.var:
                    if m.id not in self.varDict:
                        self.varDict[m.id] = m

    def RESOLVE(self):
        self.body.RESOLVE()

    def Perform_Operation(self,generator):
        return generator.generate_METHOD(self)


class FIELD(Node):
    identifier = itertools.count(1).next

    def __init__(self, name, typev, vis, app,lineno,conClass=None):
        self.id = FIELD.identifier()
        self.type = "FIELD"
        self.name = name            # FIELD NAME
        self.typev = typev          # FIELD TYPE
        self.vis = vis              # FIELD VIS
        self.app = app              # FIELD APP
        self.conClass = conClass    # Conatining class
        self.lineno = lineno
        self.offset = -1               # Field Position in memory

    def PRINT(self):
        print "FIELD %d, %s, %s, %s, %s, %s %s" % (self.id, self.name, self.conClass,
                                                self.vis,self.app ,self.typev, self.offset)

    def Perform_Operation(self,generator):
        return generator.generate_FIELD(self)

class VARIABLE(Node):
    # Need to declare for the array variables
    # This creates the variable object which contains the multiple information
    identifier = itertools.count(1).next

    def __init__(self, name, typev=None, kind=None):
        self.id = VARIABLE.identifier()
        self.type = "VARIABLE"
        self.name = name            # name of the variable
        self.typev = typev          # type of variable can be built in type or user defined
        self.kind = kind            # This indicates whether the variable is formal or local
        self.addr = ""              # This will contain the register info

    def PRINT(self):
        print "VARIABLE %d, %s, %s, %s " % (self.id, self.name, self.kind, self.typev)

    def Perform_Operation(self,generator):
        return generator.generate_VARIABLE(self)

class MFIELDS(Node):
    # This class takes the decalaration for the multiple or single fields declared
    def __init__(self, Field_decl,modifier,lineno):
        self.type = "FIELDS"
        self.modifier = modifier
        self.Field = []
        self.CREATE_FIELD(Field_decl,lineno)

    def ExtractFromModifier(self, Modlist):
        if Modlist is not None:
            lenModList = len(Modlist)
        else:
            lenModList = 0
        visible = ""  # Visibility
        app = ""      # applicability
        if (lenModList == 0):
            visible = "private"
            app     = "instance"

        elif (lenModList == 1):  # if the length of modifier is One then it contains either static
            if (Modlist[0] == "static"):
                visible = "private"
                app     = "static"
            else:
                visible = Modlist[0]
                app     = "instance"
        else:
            visible = Modlist[0]
            app     = "static"

        return [visible, app]

    # This method creates the field object from multiple field decalred in one statement
    def CREATE_FIELD(self, Field_decl,lineno):

        vis_app = self.ExtractFromModifier(self.modifier)
        for var in Field_decl:
            self.Field.append(FIELD(var.name, var.typev, vis_app[0], vis_app[1],lineno,None))


class STMT(Node):
    def __init__(self, lineno=None):
        self.type = "stmt"
        self.lineno = lineno


class IF_STMT(STMT):
    #This class creates if stmt
    def __init__(self, exprCond, thenStmt, lineno, elseStmt=None):
        super(IF_STMT, self).__init__(lineno)
        self.stmtType = "If"
        self.exprCond = exprCond
        self.thenStmt = thenStmt
        self.elseStmt = elseStmt
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        self.exprCond.PRINT()
        if(self.thenStmt is not None):
            sys.stdout.write(",")
            self.thenStmt.PRINT()
        if (self.elseStmt is not None):
            sys.stdout.write(",")
            self.elseStmt.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):

        rtype_exprCond = self.exprCond.RESOLVE(con_class,AST_TABLE)

        rtype_thenStmt = None
        if(self.thenStmt is not None):
            rtype_thenStmt = self.thenStmt.RESOLVE(con_class,AST_TABLE)

        rtype_elseStmt = None
        if(self.elseStmt is not None):
            rtype_elseStmt = self.elseStmt.RESOLVE(con_class,AST_TABLE)

        if(rtype_exprCond != "boolean"):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : type error at line %d, %s expression found instead of boolean" %(self.exprCond.lineno[0],rtype_exprCond)
            return "error"
        if(rtype_thenStmt!= None and rtype_thenStmt == "error"):
            self.exp_rtype = "error"
            return "error"
        if(rtype_elseStmt!= None and rtype_elseStmt == "error"):
            self.exp_rtype = "error"
            return "error"

        self.exp_rtype = "correct"
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_IF_STMT(self)

class WHILE_STMT(STMT):
    #This class creates while stmt
    def __init__(self, loopCond, loopBody, lineno):
        super(WHILE_STMT, self).__init__(lineno)
        self.stmtType = "While"
        self.loopCond = loopCond
        self.loopBody = loopBody
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        self.loopCond.PRINT()
        sys.stdout.write(",")
        self.loopBody.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype_loopCond = self.loopCond.RESOLVE(con_class,AST_TABLE)
        rtype_loopBody = None

        if(self.loopBody is not None):
            rtype_loopBody = self.loopBody.RESOLVE(con_class,AST_TABLE)
        if(rtype_loopCond != "boolean"):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : type error at line %d, %s expression found instead of boolean" %(self.loopCond.lineno[0],rtype_loopCond)
            return "error"
        if(rtype_loopBody != None and rtype_loopBody == "error"):
            self.exp_rtype = "error"
            return "error"
        self.exp_rtype = "correct"
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_WHILE_STMT(self)

class FOR_STMT(STMT):
    #This class creates For stmt
    def __init__(self, initExpr, loopCond, updateExpr, loopBody, lineno):
        super(FOR_STMT, self).__init__(lineno)
        self.stmtType = "For"
        self.initExpr = initExpr
        self.loopCond = loopCond
        self.updateExpr = updateExpr
        self.loopBody = loopBody
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        if(self.initExpr is not None):
            self.initExpr.PRINT()
        sys.stdout.write(",")
        if(self.loopCond is not None):
            self.loopCond.PRINT()
        sys.stdout.write(",")
        if(self.updateExpr is not None):
            self.updateExpr.PRINT()
        sys.stdout.write(",")
        if(self.loopBody is not None):
            self.loopBody.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):

        rtype_init= None
        rtype_loopcond = None
        rtype_updateExpr = None
        rtype_loopBody = None

        if(self.initExpr is not None):
            rtype_init = self.initExpr.RESOLVE(con_class,AST_TABLE)
        if(self.loopCond is not None):
            rtype_loopcond = self.loopCond.RESOLVE(con_class,AST_TABLE)
        if(self.updateExpr is not None):
            rtype_updateExpr = self.updateExpr.RESOLVE(con_class,AST_TABLE)
        if(self.loopBody is not None):
            rtype_loopBody = self.loopBody.RESOLVE(con_class,AST_TABLE)

        if(rtype_loopcond != None and rtype_loopcond != "boolean"):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : type error at line %d, %s expression found instead of boolean" %(self.loopCond.lineno[0],rtype_loopcond)
            return "error"
        if(rtype_init != None and rtype_init == "error"):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : type error at line %d, %s expression found instead of int or float" %(self.initExpr.lineno[0],rtype_init)
            return "error"
        if(rtype_updateExpr != None and rtype_updateExpr == "error"):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : type error at line %d, %s expression found instead of int or float" %(self.updateExpr.lineno[0],rtype_updateExpr)
            return "error"
        if(rtype_loopBody != None and rtype_loopBody == "error"):
            self.exp_rtype = "error"
            return "error"

        self.exp_rtype = "correct"
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_FOR_STMT(self)

class RETURN_STMT(STMT):
    #This class creates Return stmt
    def __init__(self, rValue, lineno):
        super(RETURN_STMT, self).__init__(lineno)
        self.stmtType = "Return"
        self.rValue = rValue
        self.exp_rtype = ""             #will be set after resolution

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        if(self.rValue is not None):
            self.rValue.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype = None
        if(self.rValue is not None):
            rtype = self.rValue.RESOLVE(con_class,AST_TABLE)
        else:
            rtype = "void"
        self.exp_rtype = rtype
        return rtype

    def Perform_Operation(self,generator):
        return generator.generate_RETURN_STMT(self)

class BLOCK_STMT(STMT):
    # This class creates block stmt
    def __init__(self, var, body, lineno):
        super(BLOCK_STMT, self).__init__(lineno)
        self.stmtType = "Block"
        self.var = var
        self.body = body

    #This methods look if there is any block in the block.

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        sys.stdout.write("[")
        self.PRINTBODY()
        sys.stdout.write("])")

    def PRINTBODY(self):
        if self.body is not None:
            flag=0
            for y in self.body:
                if(flag==0):
                    sys.stdout.write("\n")
                if(flag == 1):
                    sys.stdout.write(",")
                    sys.stdout.write("\n")
                flag=1
                if isinstance(y, Expression):
                    sys.stdout.write("Expr(")
                    y.PRINT()
                    sys.stdout.write(")")
                elif isinstance(y, STMT):
                    y.PRINT()
            sys.stdout.write("\n")

    def RESOLVE(self,con_class,AST_TABLE):
        if self.body is not None:
            error = 0
            for y in self.body:
                if isinstance(y,Expression):
                    if(y.RESOLVE(con_class,AST_TABLE) == "error"):
                        error=1
                        #print >> sys.stderr, "error : incompatible type in statement at lineno %d" %(y.lineno[0])
                elif isinstance(y,STMT):
                    if(y.RESOLVE(con_class,AST_TABLE) == "error"):
                        error=1
                        #print >> sys.stderr, "error : incompatible type in statement at lineno %d" %(y.lineno[0])
            if(error == 1):
                return "error"
            else:
                return "correct"
        else:
            return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_BLOCK_STMT(self)

class BREAK_STMT(STMT):
    #This class creates Break stmt
    def __init__(self, lineno):
        super(BREAK_STMT, self).__init__(lineno)
        self.stmtType = "Break"

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_BREAK_STMT(self)

class CONTINUE_STMT(STMT):
    #This class creates continue stmt
    def __init__(self, lineno):
        super(CONTINUE_STMT, self).__init__(lineno)
        self.stmtType = "Continue"

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_CONTINUE_STMT(self)

class SKIP_STMT(STMT):
    #This class creates a skip statement
    def __init__(self, lineno):
        super(SKIP_STMT, self).__init__(lineno)
        self.stmtType = "Skip"

    def PRINT(self):
        sys.stdout.write(self.stmtType)
        sys.stdout.write("(")
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        return "correct"

    def Perform_Operation(self,generator):
        return generator.generate_SKIP_STMT(self)

class Expression(Node):
    def __init__(self, lineno=None):
        self.type = "expr"
        self.lineno = lineno


class CONST_EXP(Expression):
    # This class creates the object for the CONSTEXP
    def __init__(self,typeCONST ,value, lineno,exp_rtype):
        super(CONST_EXP, self).__init__(lineno)
        self.expType = "Constant"
        self.typeCONST = typeCONST  # typeCONST can be INTEGER,FLOAT,NULL,TRUE,FALSE
        self.value = value
        self.exp_rtype = exp_rtype

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write(self.typeCONST)
        sys.stdout.write("(")
        sys.stdout.write(str(self.value))
        sys.stdout.write(")")
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        return self.exp_rtype

    def Perform_Operation(self,generator):
        return generator.generate_CONST_EXP(self)

class VAR_EXP(Expression):
    # This class creates variable object which contains the ID of the variable

    def __init__(self, var, id, lineno):
        super(VAR_EXP, self).__init__(lineno)
        self.var = var
        self.expType = "Variable"
        self.id = id
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(%i)" % self.id)

    def RESOLVE(self,con_class,AST_TABLE):
        self.exp_rtype = self.var.typev
        return self.var.typev

    def Perform_Operation(self,generator):
        return generator.generate_VAR_EXP(self)

class UNARY_EXP(Expression):
    # The class creates the Unary expression object which contains the Op and exp
    operatorMap = {"-": "uminus", "!": "neg"}

    def __init__(self, Op, exp, lineno):
        super(UNARY_EXP, self).__init__(lineno)
        self.expType = "Unary"
        self.Op = UNARY_EXP.operatorMap[Op]  # This OP can be UMINUS or NEG
        self.exp = exp                       # This is the object of the expression
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write(self.Op)
        sys.stdout.write(",")
        self.exp.PRINT()
        sys.stdout.write(")")
        return ""

    def RESOLVE(self,con_class,AST_TABLE):
        if self.Op is "uminus":
            rtype = self.exp.RESOLVE(con_class,AST_TABLE)
            if(rtype == "int" or rtype == "float"):
                self.exp_rtype = rtype
                return rtype
            else:
                print >> sys.stderr, "error : type error at line %d expected int or float instead of %s" %(self.exp.lineno[0],rtype)
                self.exp_rtype = "error"
                return "error"

        elif self.Op is "neg":
            rtype = self.exp.RESOLVE(con_class,AST_TABLE)
            if(rtype == "boolean"):
                self.exp_rtype = "boolean"
                return rtype
            else:
                print >> sys.stderr, "error : type error at line %d expected boolean instead of %s" %(self.exp.lineno[0],rtype)
                self.exp_rtype = "error"
                return "error"
        else:
            self.exp_rtype = "error"
            return "error"

    def Perform_Operation(self,generator):
        return generator.generate_UNARY_EXP(self)

class BINARY_EXP(Expression):
    # The class creates the Binary expression object which contains the Op value
    # and the two expression on which the Op is applied
    operatorMap = {"+": "add",
                   "-": "sub",
                   "*": "mul",
                   "/": "div",
                   "&&": "and",
                   "||": "or",
                   "==": "eq",
                   "!=": "neq",
                   "<": "lt",
                   ">": "gt",
                   "<=": "leq",
                   ">=": "geq"
                   }

    def __init__(self, Op, exp1, exp2, lineno):
        super(BINARY_EXP, self).__init__(lineno)
        self.expType = "Binary"
        self.Op = BINARY_EXP.operatorMap[Op]
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write(self.Op)
        sys.stdout.write(",")
        self.exp1.PRINT()
        sys.stdout.write(",")
        self.exp2.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype1 = self.exp1.RESOLVE(con_class,AST_TABLE)
        rtype2 = self.exp2.RESOLVE(con_class,AST_TABLE)

        if(self.Op == "add" or self.Op == "sub" or self.Op == "mul" or self.Op == "div"):

            if(rtype1 == "int" and rtype2 == "int"):
                self.exp_rtype = "int"
                return "int"
            elif(rtype1 == "float" and rtype2 == "float"):
                self.exp_rtype = "float"
                return "float"
            elif((rtype1 == "int" and rtype2 == "float") or (rtype1 == "float" and rtype2 == "int")):
                self.exp_rtype = "float"
                return "float"
            else:
                self.exp_rtype = "error"
                print >> sys.stderr, "error : incompatible type at line %d expression type should be int or float instead %s %s" %(self.exp1.lineno[0],rtype1,rtype2)
                return "error"

        elif(self.Op == "and" or self.Op == "or"):

            if(rtype1 == "boolean" and rtype2 == "boolean"):
                self.exp_rtype = "boolean"
                return "boolean"
            else:
                print >> sys.stderr, "error : incompatible type at line %d expected both boolean but found %s %s" %(self.exp1.lineno[0],rtype1,rtype2)

                self.exp_rtype = "error"
                return "error"

        elif(self.Op == "lt" or self.Op == "leq" or self.Op == "gt" or self.Op == "geq"):
            if(rtype1 == "int" and rtype2 == "int"):
                self.exp_rtype = "boolean"
                return "boolean"
            elif(rtype1 == "float" and rtype2 == "float"):
                self.exp_rtype = "boolean"
                return "boolean"
            else:
                print >> sys.stderr, "error : type error at line %d both expression should of type int or float instead of %s %s" %(self.exp1.lineno[0],rtype1,rtype2)
                self.exp_rtype = "error"
                return "error"

        elif(self.Op == "eq" or self.Op == "neq"):
            if( self.Determine_type_relation(rtype1,rtype2,AST_TABLE) == 1 or self.Determine_type_relation(rtype1,rtype2,AST_TABLE) ==  2):
                self.exp_rtype = "boolean"
                return "boolean"
            else:
                print >> sys.stderr, "error : incompatible types at lineno %d" %(self.exp1.lineno[0])
                self.exp_rtype = "error"
                return "error"

    def Determine_type_relation(self,rtype1,rtype2,AST_TABLE):
        if(rtype1 == "error"): return -1
        if(rtype2 == "error"): return -1
        t1 = self.Extracttype(rtype1)
        t2 = self.Extracttype(rtype2)

        if(t1 == None and t2 !=None):
            if(rtype1 == "null"):
                return 2
            else:
                return -1
        elif(t1 !=None and t2 ==None):
            if(rtype2 == "null"):
                return 1
            else:
                return -1
        elif (t1 != None and t2 != None):
            return self.Determine_type_relation(t1,t2,AST_TABLE)
        else:
            if (rtype1 in AST_TABLE.subtypetuple[rtype2]): return 1     #t2 is subtype of t1
            elif (rtype2 in AST_TABLE.subtypetuple[rtype1]): return 2   #t1 is subtype of t2
            else : return -1

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

    def Perform_Operation(self,generator):
        return generator.generate_BINARY_EXP(self)

class ASSIGN_EXP(Expression):
    # The class creates assign expression object which contains the two expression

    def __init__(self, exp1, exp2, lineno):
        super(ASSIGN_EXP, self).__init__(lineno)
        self.expType = "Assign"
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp_rtype = ""
        self.rtype1 = ""
        self.rtype2 = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        self.exp1.PRINT()
        sys.stdout.write(",")
        self.exp2.PRINT()
        sys.stdout.write(",")
        sys.stdout.write(self.rtype1)
        sys.stdout.write(",")
        sys.stdout.write(self.rtype2)
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype1 = self.exp1.RESOLVE(con_class,AST_TABLE)
        rtype2 = self.exp2.RESOLVE(con_class,AST_TABLE)

        if(rtype2 != "error" and rtype1 != "error" and self.Determine_type_relation(rtype1,rtype2,AST_TABLE) == 1 ):
            self.rtype1 = rtype1
            self.rtype2 = rtype2
            self.exp_rtype = rtype2
            return rtype2
        else:
            print >> sys.stderr, "error : incompatible types at line %d in assign expression %s , %s " %(self.exp1.lineno[0],rtype1,rtype2)
            self.exp_rtype = "error"
            return "error"

    def Determine_type_relation(self,rtype1,rtype2,AST_TABLE):
        if(rtype1 == "error"): return -1
        if(rtype2 == "error"): return -1
        t1 = self.Extracttype(rtype1)
        t2 = self.Extracttype(rtype2)

        if(t1 == None and t2 !=None):
            if(rtype1 == "null"):
                return 2
            else:
                return -1
        elif(t1 !=None and t2 ==None):
            if(rtype2 == "null"):
                return 1
            else:
                return -1
        elif (t1 != None and t2 != None):
            return self.Determine_type_relation(t1,t2,AST_TABLE)
        else:

            if (rtype1 in AST_TABLE.subtypetuple[rtype2]): return 1     #t2 is subtype of t1
            elif (rtype2 in AST_TABLE.subtypetuple[rtype1]): return 2   #t1 is subtype of t2
            else : return -1

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

    def Perform_Operation(self,generator):
        return generator.generate_ASSIGN_EXP(self)


class AUTO_EXP(Expression):
    # The class creates Auto expression object which contains the Op and expression and
    # the order in which it is applied

    def __init__(self, exp, Op, order, lineno):
        super(AUTO_EXP, self).__init__(lineno)
        self.expType = "Auto"
        self.exp = exp
        self.Op = Op        # Op can be ++,--
        self.order = order  # order can post or pre
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        self.exp.PRINT()
        sys.stdout.write(",")
        sys.stdout.write(self.Op)
        sys.stdout.write(",")
        sys.stdout.write(self.order)
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype = self.exp.RESOLVE(con_class,AST_TABLE)
        if(rtype == "int" or rtype == "float"):
            self.exp_rtype = rtype
            return rtype
        else:
            print >> sys.stderr, "error : type error at line %d int or float expected instead of %s " %(self.exp.lineno[0],rtype)
            self.exp_rtype = "error"
            return "error"

    def Perform_Operation(self,generator):
        return generator.generate_AUTO_EXP(self)

class FIELD_EXP(Expression):
    # This class creates the Field expression object which contains the expression and ID
    # of the field access

    def __init__(self, name, exp, lineno):
        super(FIELD_EXP, self).__init__(lineno)
        self.expType = "Field-access"
        self.exp = exp
        self.name = name
        self.exp_rtype = ""
        self.resolvedID = -1

    def PRINT(self):
        if self.exp is not None:
            sys.stdout.write(self.expType)
            sys.stdout.write("(")
            self.exp.PRINT()
            sys.stdout.write(",")
            sys.stdout.write(self.name)
            sys.stdout.write(",")
            sys.stdout.write(str(self.resolvedID))
            sys.stdout.write(")")

        else:
            sys.stdout.write(self.expType)
            sys.stdout.write("(")
            sys.stdout.write(self.name)
            sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype = self.exp.RESOLVE(con_class,AST_TABLE)
        if(rtype == "error"):
            return "error"
        #If rtype is User it indicates instance attribute
        #Check for the field starting from the containing class upto all super class
        #and if found the match return the type of the resolved field

        if rtype[:5] == "User(":
            key = rtype[5:-1]
            CLASS = AST_TABLE.GetClassRef(key)
            while(True):
                for field in CLASS.Fields:
                    if(field.name == self.name and field.app == "instance"):
                        if(con_class.name == CLASS.name or field.vis == "public"):
                            self.exp_rtype = field.typev
                            self.resolvedID = field.id
                            return field.typev

                if(CLASS.super_name is ""):   #No more superclass to look in
                    break
                CLASS = AST_TABLE.GetClassRef(CLASS.super_name)
            self.exp_rtype = "error"
            print >> sys.stderr, "error : cannot find symbol %s at lineno %d  "%(self.name,self.lineno[0])
            return "error"

        elif rtype[:14] == "class-literal(":              #rtype = "class-literal"
            key = rtype[14:-1]
            CLASS = AST_TABLE.GetClassRef(key)
            while(True):
                for field in CLASS.Fields:
                    if(field.name == self.name and field.app == "static"):
                        if(con_class.name == CLASS.name or field.vis == "public"):
                            self.exp_rtype = field.typev
                            self.resolvedID = field.id
                            return field.typev

                if(CLASS.super_name is ""):
                    break
                CLASS = AST_TABLE.GetClassRef(CLASS.super_name)
            self.exp_rtype = "error"
            print >> sys.stderr, "error : cannot find symbol at %s lineno %d  "%(self.name,self.lineno[0])
            return "error"
        else:
            return "error"

    def Perform_Operation(self,generator):
        return generator.generate_FIELD_EXP(self)

class METHOD_CALL_EXP(Expression):
    # This class creates the Method call expression object which contains the
    # expression, ID and arguments of the method

    def __init__(self, exp, arguments, lineno):
        super(METHOD_CALL_EXP, self).__init__(lineno)
        self.expType = "Method-call"
        self.exp = exp.exp
        self.name = exp.name
        self.arguments = arguments
        self.resolveID = ""
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        self.exp.PRINT()
        sys.stdout.write(",")
        sys.stdout.write(self.name)
        sys.stdout.write(",")
        sys.stdout.write("[")
        self.PRINTARG()
        sys.stdout.write("]")
        sys.stdout.write(",")
        sys.stdout.write(str(self.resolveID))
        sys.stdout.write(")")

    def PRINTARG(self):
        if (self.arguments is not None):
            flag = 0
            for x in self.arguments:
                if (flag != 0):
                    sys.stdout.write(",")
                flag = 1
                x.PRINT()
        else:
            sys.stdout.write("")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype = self.exp.RESOLVE(con_class,AST_TABLE)

        if(rtype == "error"):
            self.exp_rtype = "error"
            return "error"

        if(rtype[:5] == "User("):
            key = rtype[5:-1]

            CLASS = AST_TABLE.GetClassRef(key)
            param_subtuple = self.gettype_of_expression(self.arguments,con_class,AST_TABLE)

            if("error" in param_subtuple):
                self.exp_rtype = "error"
                return "error"

            method_match = None
            while(True):
                for METHOD in CLASS.Methods:
                    if(METHOD.name == self.name and METHOD.app == "instance"):              #No else condition we can find match in other super classes
                        if(con_class.name == CLASS.name or METHOD.vis == "public"):
                            method_param = self.gettype_of_METHOD(METHOD.param)
                            if(self.issubtype(param_subtuple,method_param,AST_TABLE)):
                                if(method_match == None):
                                    method_match = METHOD
                                else:
                                    t1 = self.gettype_of_METHOD(method_match.param) #previous matched tuple
                                    k1 = self.issubtype(method_param,t1,AST_TABLE)
                                    k2 = self.issubtype(t1,method_param,AST_TABLE)
                                    if( k1 and k2):
                                        if(self.Determine_type_relation(METHOD.conClass,method_match.conClass,AST_TABLE) == 2):
                                            method_match = METHOD
                                    elif(k1):
                                        method_match = METHOD
                                    elif(not k1 and not k2):
                                        self.exp_rtype = "error"
                                        print >> sys.stderr, "error : reference to %s is ambiguous at lineno %d" %(self.name,self.lineno[0])
                                        return "error"

                if(CLASS.super_name == ""):
                    break
                CLASS = AST_TABLE.GetClassRef(CLASS.super_name)

            if(method_match is None):
                print >> sys.stderr,"error : no matching method found for the %s method at lineno %d" %(self.name,self.lineno[0])
                self.exp_rtype = "error"
                return "error"
            else:
                self.exp_rtype = method_match.rtype
                self.resolveID = method_match.id
                return method_match.rtype

        elif(rtype[:14] == "class-literal("):
            key = rtype[14:-1]
            CLASS = AST_TABLE.GetClassRef(key)
            param_subtuple = self.gettype_of_expression(self.arguments,con_class,AST_TABLE)

            if("error" in param_subtuple):
                self.exp_rtype = "error"
                return "error"

            method_match = None
            while(True):
                for METHOD in CLASS.Methods:
                    if(METHOD.name == self.name and METHOD.app == "static"):
                        if(con_class.name == CLASS.name or METHOD.vis == "public"):
                            method_param = self.gettype_of_METHOD(METHOD.param)
                            if(self.issubtype(param_subtuple,method_param,AST_TABLE)):
                                if(method_match == None):
                                    method_match = METHOD
                                else:
                                    t1 = self.gettype_of_METHOD(method_match.param)
                                    k1 = self.issubtype(method_param,t1,AST_TABLE)
                                    k2 = self.issubtype(t1,method_param,AST_TABLE)
                                    if( k1 and k2):
                                        if(self.Determine_type_relation(METHOD.conClass,method_match.conClass,AST_TABLE) == 2):
                                            method_match = METHOD
                                    elif(k1):
                                        method_match = METHOD
                                    elif(not k1 and not k2):
                                        self.exp_rtype = "error"
                                        print >> sys.stderr, "error : reference to %s is ambiguous at lineno %d" %(self.name,self.lineno[0])
                                        return "error"

                if(CLASS.super_name == ""):
                    break
                CLASS = AST_TABLE.GetClassRef(CLASS.super_name)

            if(method_match is None):
                print >> sys.stderr,"error : no matching method found for the %s method at lineno %d" %(self.name,self.lineno[0])
                self.exp_rtype = "error"
                return "error"
            else:
                self.exp_rtype = method_match.rtype
                self.resolveID = method_match.id
                return method_match.rtype
        else:
            print >> sys.stderr,"error : method invocation cannot be applied to %s type at lineno %d" %(rtype,self.lineno[0])
            self.exp_rtype = "error"
            return "error"

    def Determine_type_relation(self,rtype1,rtype2,AST_TABLE):
        if(rtype1 == "error"): return -1
        if(rtype2 == "error"): return -1
        t1 = self.Extracttype(rtype1)
        t2 = self.Extracttype(rtype2)
        if(t1 == None and t2 !=None):
            if(rtype1 == "null"):
                return 2
            else:
                return -1
        elif(t1 !=None and t2 ==None):
            if(rtype2 == "null"):
                return 1
            else:
                return -1
        elif (t1 != None and t2 != None):
           return  self.Determine_type_relation(t1,t2,AST_TABLE)
        else:
            if(rtype1 in AST_TABLE.subtypetuple[rtype2] and rtype2 in AST_TABLE.subtypetuple[rtype1]):
                return 3                                                #t1 and t2 are equal
            elif (rtype1 in AST_TABLE.subtypetuple[rtype2]): return 1   #t2 is subtype of t1
            elif (rtype2 in AST_TABLE.subtypetuple[rtype1]): return 2   #t1 is subtype of t2
            else : return -1

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

    def gettype_of_expression(self,list,con_class,AST_TABLE):
        type_of_args = []                   #This list will contain the type of all parameter of method
        if (list is not None):
            for x in list:
                resol = x.RESOLVE(con_class,AST_TABLE)
                if resol != "error":
                    type_of_args = type_of_args + [resol]
                else:
                    type_of_args = type_of_args + ["error"]
        return type_of_args

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
        else:
            return False

    def Perform_Operation(self,generator):
        return generator.generate_METHOD_CALL_EXP(self)

class NEW_OBJ_EXP(Expression):
    # This class creates the New-Object expression object which contains the
    # class name exp and the arguments

    def __init__(self, cname, arguments, lineno):
        super(NEW_OBJ_EXP, self).__init__(lineno)
        self.expType = "New-object"
        self.cname = cname
        self.arguments = arguments
        self.resolveID = -1
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write(self.cname)
        sys.stdout.write(",")
        sys.stdout.write("[")
        self.PRINTARG()
        sys.stdout.write("]")
        sys.stdout.write(",")
        sys.stdout.write(str(self.resolveID))
        sys.stdout.write(")")

    def PRINTARG(self):
        if (self.arguments is not None):
            flag = 0
            for x in self.arguments:
                if (flag != 0):
                    sys.stdout.write(",")
                flag = 1
                x.PRINT()
        else:
            sys.stdout.write("")

    def RESOLVE(self,con_class,AST_TABLE):
        CLASS = AST_TABLE.GetClassRef(self.cname)
        param_subtuple = self.gettype_of_expression(self.arguments,con_class,AST_TABLE)

        if("error" in param_subtuple):
            self.exp_rtype = "error"
            return "error"

        constructor_match = None

        for CONSTRUCTOR in CLASS.CConstructors:
            if(CONSTRUCTOR.name == self.cname):
                if(con_class.name == CLASS.name or CONSTRUCTOR.vis == "public"):
                    con_arg_tuple = self.gettype_of_METHOD(CONSTRUCTOR.param)
                    if(self.issubtype(param_subtuple,con_arg_tuple,AST_TABLE)):
                        if(constructor_match == None):
                            constructor_match = CONSTRUCTOR
                        else:

                            t1 = self.gettype_of_METHOD(constructor_match.param) #previous matched tuple
                            k1 = self.issubtype(con_arg_tuple,t1,AST_TABLE)
                            k2 = self.issubtype(t1,con_arg_tuple,AST_TABLE)
                            if( k1 and k2): #There can be no two constructor with same type tuple
                                print >> sys.stderr, "error : constructor at lineno %d and %d have same args type" %(constructor_match.lineno[0],CONSTRUCTOR.lineno[0])
                            elif(k1):
                                constructor_match = CONSTRUCTOR
                            elif(not k1 and not k2):
                                self.exp_rtype = "error"
                                print >> sys.stderr, "error : ambiguous reference for the new object at lineno %d" %(constructor_match.lineno[0])
                                return "error"

        if(constructor_match == None):
            self.exp_rtype = "error"
            print >> sys.stderr, "error : cannot find matching constructor for new object at line no %d" %(self.lineno[0])
            return "error"
        else:
            self.resolveID = constructor_match.id
            self.exp_rtype = "User("+constructor_match.name+")"
            return "User("+constructor_match.name+")"

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
        else:
            return False

    def Determine_type_relation(self,rtype1,rtype2,AST_TABLE):
        if(rtype1 == "error"): return -1
        if(rtype2 == "error"): return -1
        t1 = self.Extracttype(rtype1)
        t2 = self.Extracttype(rtype2)
        if(t1 == None and t2 !=None):
            if(rtype1 == "null"):
                return 2
            else:
                return -1
        elif(t1 !=None and t2 ==None):
            if(rtype2 == "null"):
                return 1
            else:
                return -1
        elif (t1 != None and t2 != None):
           return  self.Determine_type_relation(t1,t2,AST_TABLE)
        else:
            if(rtype1 in AST_TABLE.subtypetuple[rtype2] and rtype2 in AST_TABLE.subtypetuple[rtype1]):
                return 3                                                #t1 and t2 are equal
            elif (rtype1 in AST_TABLE.subtypetuple[rtype2]): return 1   #t2 is subtype of t1
            elif (rtype2 in AST_TABLE.subtypetuple[rtype1]): return 2   #t1 is subtype of t2
            else : return -1

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

    def gettype_of_expression(self,list,con_class,AST_TABLE):
        type_of_args = []                   #This list will contain the type of all parameter of method
        if (list is not None):
            for x in list:
                resol = x.RESOLVE(con_class,AST_TABLE)
                if resol != "error":
                    type_of_args = type_of_args + [resol]
                else:
                    type_of_args = type_of_args + ["error"]

        return type_of_args

    def gettype_of_METHOD(self,list):
        type_of_args = []                   #This list will contain the type of all parameter of method
        if (list is not None):
            for x in list:
                type_of_args = type_of_args + [x.typev]
        return type_of_args

    def Perform_Operation(self,generator):
        return generator.generate_NEW_OBJ_EXP(self)

class THIS_EXP(Expression):
    #This class creates THIS_EXP Node
    def __init__(self, lineno):
        super(THIS_EXP, self).__init__(lineno)
        self.expType = "This"
        self.rtype = ""
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)

    def RESOLVE(self,con_class,AST_TABLE):
        self.exp_rtype = "User("+con_class.name+")"
        return "User("+con_class.name+")"

    def Perform_Operation(self,generator):
        return generator.generate_THIS_EXP(self)

class SUPER_EXP(Expression):
    #This class creates SUPER_EXP Node
    def __init__(self, lineno):
        super(SUPER_EXP, self).__init__(lineno)
        self.expType = "Super"
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)

    def RESOLVE(self,con_class,AST_TABLE):
        if con_class.super_name != "":
            self.exp_rtype = "User("+con_class.super_name+")"
            return "User("+con_class.super_name+")"
        else:
            print >> sys.stderr , "error : super class doesn't exist at lineno %d"%(self.lineno[0])
            self.exp_rtype = "error"
            return "error"

    def Perform_Operation(self,generator):
        return generator.generate_SUPER_EXP(self)

class CLASS_REF_EXP(Expression):
    #This class creates CLASS_REF_EXP Node
    def __init__(self, cname, lineno):
        super(CLASS_REF_EXP, self).__init__(lineno)
        self.expType = "Class-reference"
        self.cname = cname
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write("class-literal")
        sys.stdout.write("(")
        sys.stdout.write(self.cname)
        sys.stdout.write(")")
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        self.exp_rtype = "class-literal("+self.cname+")"
        return "class-literal("+self.cname+")"

    def Perform_Operation(self,generator):
        return generator.generate_CLASS_REF_EXP(self)

class ARR_ACC_EXP(Expression):
    #This class     creates ARR_ACC_EXP Node
    def __init__(self, exp1, exp2, lineno):
        super(ARR_ACC_EXP, self).__init__(lineno)
        self.expType = "Array-access"
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        self.exp1.PRINT()
        sys.stdout.write(",")
        self.exp2.PRINT()
        sys.stdout.write(")")

    def RESOLVE(self,con_class,AST_TABLE):
        rtype1 = self.exp1.RESOLVE(con_class,AST_TABLE)
        rtype2 = self.exp2.RESOLVE(con_class,AST_TABLE)
        #print "In Array ACcess resolve : ",rtype1,rtype2
        if(rtype2 == "int"):
            if(rtype1[:6] == "array("):
                rtype1 = rtype1[6:-1]
                self.exp_rtype = rtype1
                return rtype1
            else:
                return "error"
        else:
            self.exp_rtype = "error"
            return "error"

    def Perform_Operation(self,generator):
        return generator.generate_ARR_ACC_EXP(self)

class NEW_ARR_EXP(Expression):
    #This class creates NEW_ARR_EXP object
    def __init__(self, dimension, basetype, lineno):
        super(NEW_ARR_EXP, self).__init__(lineno)
        self.expType = "New-array"
        self.dimension = dimension
        self.basetype = basetype
        self.exp_rtype = ""

    def PRINT(self):
        sys.stdout.write(self.expType)
        sys.stdout.write("(")
        sys.stdout.write(self.basetype)
        sys.stdout.write(",")
        sys.stdout.write("[")
        self.PRINTDIMENSION()
        sys.stdout.write("]")
        sys.stdout.write(")")

    def PRINTDIMENSION(self):
        if (self.dimension is not None):
            flag = 0
            for x in self.dimension:
                if (flag != 0):
                    sys.stdout.write(",")
                flag = 1
                x.PRINT()
        else:
            sys.stdout.write("")

    def RESOLVE(self,con_class,AST_TABLES):
        if(self.dimension is not None):
            for x in self.dimension:
                if(x.RESOLVE(con_class,AST_TABLES) != "int"):
                    self.exp_rtype = "error"
                    return "error"
            rtype = self.basetype
            for x in self.dimension:
                rtype = "array("+rtype+")"

            self.exp_rtype = rtype
            return self.exp_rtype

    def Perform_Operation(self,generator):
        return generator.generate_NEW_ARR_EXP(self)