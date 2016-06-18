from AST import *
from absmc import *
from SSA import *
class Mapp (object):

    def __init__(self):
        self.ioperatorMap = {"add" :"add",
                   "sub": "sub",
                   "mul": "mul",
                   "div": "div",
                   "and": "and",
                   "or": "or",
                   "eq": "seq",
                   "neq": "sne",
                   "lt": "slt",
                   "gt": "sgt",
                   "leq": "sle",
                   "geq": "sge",

                   }
        self.foperatorMap = {
                   "add" :"add.s",
                   "sub": "sub.s",
                   "mul": "mul.s",
                   "div": "div.s",
                   "eq":"seq.s",
                   "neq":"sne.s",
                   "lt": "slt.s",
                   "gt": "sgt.s",
                   "leq": "sle.s",
                   "geq": "sge.s"

                   }
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

class Code_Generator(object):

    def __init__(self,AST_TABLE,fileName):
        self.absmc = Abstract_Regsiter_Machine(fileName)
        self.Mapp = Mapp()
        self.tab = 0
        self.nearestLoopBegin = []
        self.nearestLoopEnd = []
        self.AST_TABLE = AST_TABLE
        self.ClassMemInfo = {}
        self.PreProcess()
        self.static = 0
        self.InstructionSet = {}
        self.ProgramCounter = -1

    def printDict(self):
        print "Instruction set"
        print self.ProgramCounter

        for key in self.InstructionSet:
            print key
            print(self.InstructionSet[key].irnode)

    def insert_instruction(self,irnode):

        self.ProgramCounter = self.ProgramCounter + 1
        self.InstructionSet[self.ProgramCounter] = IRNode(irnode)

    def PreProcess(self):
        #compute the number of memory cells required for the given
        #assumption
        #class name cannot be used before its decalaration

        for CLASS in self.AST_TABLE.children:

            if(CLASS.super_name == ""):
                self.ClassMemInfo[CLASS.name] = len(CLASS.Fields)
            else:
                self.ClassMemInfo[CLASS.name] = len(CLASS.Fields) \
                                                + self.ClassMemInfo[CLASS.super_name]

    def leave_tab(self):
        for num in range(0,self.tab):
            self.absmc.write("\t")

    def generate_CLASS(self,CLASS):
        #generate the offset for the fields
        counter = 0
#     for classes in self.AST_TABLE.subtypetuple[CLASS.name]:
#         print "classes list :",classes
        for class_element in reversed(self.AST_TABLE.subtypetuple[CLASS.name]):
            #print class_element
            class_ref = self.AST_TABLE.GetClassRef(class_element)
            if(class_ref == None):
                continue
            start_offset = 0
            if(class_ref.super_name != ""):
                start_offset = self.ClassMemInfo[class_ref.super_name]
                
            for field in class_ref.Fields:
                if(field.offset == -1):
                    field.offset = start_offset + counter
                    counter = counter + 1
                if(field.app == "static"):
                    field.offset = self.static
                    self.static = self.static + 1
        return

    def generate_METHOD(self,METHOD):


        if(METHOD.name == "main"):
            str1 = "main_entry_point: "
        else:
            str1 = "M_%s_%d: "%(METHOD.name,METHOD.id)

        if(METHOD.name[0:4] == "scan" or METHOD.name[0:5] == "print"):
            return

        self.absmc.write(str1)
        self.insert_instruction((str1,"","",""))


        self.absmc.write("\n")
        self.tab += 1

        self.leave_tab()
        self.absmc.write("subu $sp, $sp, 32 \t# Stack Frame setup \n")
        self.insert_instruction(("subu","$sp","$sp","32"))

        self.leave_tab()
        self.absmc.write("sw $ra, 28($sp) \t# Preserve the return address\n")
        self.insert_instruction(("sw","$ra","28($sp)",""))

        self.leave_tab()
        self.absmc.write("sw $fp, 24($sp) \t# Preserve the frame pointer\n")
        self.insert_instruction(("sw","$fp","24($sp)",""))

        self.leave_tab()
        self.absmc.write("addu $fp, $sp, 32 \t# move frame pointer to the base of frame\n")
        self.insert_instruction(("addu","$fp","$sp","32"))

        self.absmc.write("\n")
        self.tab -= 1

        self.absmc.arg = 0
        counter = 0
        addr = 20
        if(METHOD.app == "instance" and METHOD.param is not None):
            self.absmc.alloc_argument_register()
            counter += 1
            for y in METHOD.param:
                if(y.kind == "formal"):
                    if(counter < 4):
                        y.addr = self.absmc.alloc_argument_register()
                        counter += 1
                    else:
                        y.addr = self.absmc.Generate_new_temporary()
                        self.tab += 1
                        self.leave_tab()
                        self.absmc.write("lw $%s, %s($sp)\n"%(y.addr,str(addr)))
                        self.insert_instruction(("lw","$%s"%(y.addr),"%s($sp)"%(str(addr)),""))

                        addr -= 4
                        self.tab -= 1
            self.absmc.write("\n")
        elif(METHOD.app == "static" and METHOD.param is not None):
            for y in METHOD.param:
                if(y.kind == "formal"):
                    y.addr = self.absmc.alloc_argument_register()
    
        if(METHOD.body is not None):
            self.absmc.register = 0
            self.absmc.fregister = 0
            self.tab = self.tab + 1
            METHOD.body.Perform_Operation(self)
            self.tab = self.tab - 1

        self.tab += 1
        self.tab -= 1
    def generate_CONSTRUCTOR(self,CONSTRUCTOR):
        self.absmc.write("C_%d: "%(CONSTRUCTOR.id))

        str = "C_%d: "%(CONSTRUCTOR.id)
        self.insert_instruction((str,"","",""))

        self.absmc.write("\n")
        self.tab += 1

        self.leave_tab()
        self.absmc.write("subu $sp, $sp, 32 \t# Stack Frame setup \n")
        self.insert_instruction(("subu","$sp","$sp","32"))

        self.leave_tab()
        self.absmc.write("sw $ra, 28($sp) \t# Preserve the return address\n")
        self.insert_instruction(("sw","$ra","28($sp)",""))

        self.leave_tab()
        self.absmc.write("sw $fp, 24($sp) \t# Preserve the frame pointer\n")
        self.insert_instruction(("sw","$fp","24($sp)",""))

        self.leave_tab()
        self.absmc.write("addu $fp, $sp, 32 \t# move frame pointer to the base of frame\n")
        self.insert_instruction(("addu","$fp","$sp","32"))

        self.absmc.write("\n")
        self.tab -= 1



        self.absmc.write("\n")
        self.absmc.arg = 0
        if(CONSTRUCTOR.param is not None):
            self.absmc.alloc_argument_register()
            for y in CONSTRUCTOR.varDict:
                if(CONSTRUCTOR.varDict[y].kind == "formal"):
                    CONSTRUCTOR.varDict[y].addr = self.absmc.alloc_argument_register()

        if(CONSTRUCTOR.body is not None):
            self.absmc.register = 0
            self.absmc.fregister = 0
            self.tab = self.tab + 1
            CONSTRUCTOR.body.Perform_Operation(self)
            self.tab = self.tab - 1

        self.tab = self.tab + 1

        self.absmc.write("\n")
        self.absmc.write("\n")

        self.leave_tab()
        self.absmc.write("lw $ra, 28($sp) \t#restore the return address\n")
        self.insert_instruction(("lw","$ra","28($sp)",""))

        self.leave_tab()
        self.absmc.write("lw $fp, 24($sp) \t#restore the frame pointer\n")
        self.insert_instruction(("lw","$fp","24($sp)",""))

        self.leave_tab()
        self.absmc.write("addu $sp, $sp, 32 \t#restore the stack pointer\n")
        self.insert_instruction(("addu","$sp","$sp","32"))


        self.leave_tab()
        self.absmc.write("jr $ra\t\t\t\t#Return\n")
        self.insert_instruction(("jr","$ra","",""))
        self.tab = self.tab - 1

    def generate_FIELD(self,FIELD):
        pass

    def generate_VARIABLE(self,Variable):
        pass

    def generate_IF_STMT(self,ISTMT):
        #if_begin = self.absmc.Generate_new_label()
        if_end = self.absmc.Generate_new_label()
        else_begin = self.absmc.Generate_new_label()
        # self.absmc.write(""+if_begin+":\t\t\t\t#Beginning of if block\n")
        # self.insert_instruction((if_begin,"","",""))

        self.tab = self.tab + 1
        exprReg = ISTMT.exprCond.Perform_Operation(self)
        self.leave_tab()
        if(ISTMT.elseStmt):
            self.absmc.write("beqz $%s, %s#branch to else\n"%(exprReg[0],else_begin))
            self.insert_instruction(("beqz","$"+exprReg[0],else_begin,""))
        else:
            self.absmc.write("beqz $%s, %s\n"%(exprReg[0],if_end))
            self.insert_instruction(("beqz","$"+exprReg[0],if_end,""))

        ISTMT.thenStmt.Perform_Operation(self)
        self.leave_tab()
        self.absmc.write("b %s \n"%if_end)
        self.insert_instruction(("b",if_end,"",""))

        if(ISTMT.elseStmt):
            self.absmc.write(else_begin+":\t\t\t\t#Beginning of Else Block\n")
            self.insert_instruction((else_begin,"","",""))

            self.tab = self.tab + 1
            ISTMT.elseStmt.Perform_Operation(self)
            self.tab -=1

        self.tab = self.tab - 1        
        self.absmc.write(""+if_end+":\t\t\t\t#End of if block\n")
        self.insert_instruction((if_end,"","",""))

    def generate_WHILE_STMT(self,WSTMT):
        while_begin = self.absmc.Generate_new_label()
        while_end = self.absmc.Generate_new_label()
        self.absmc.write(""+while_begin+":\t\t\t\t#Beginning of while loop\n")
        self.insert_instruction((while_begin,"","",""))

        self.tab +=1
        loopCondReg = WSTMT.loopCond.Perform_Operation(self)
        self.leave_tab()
        self.absmc.write("beqz $%s, %s\n"%(loopCondReg[0],while_end))
        self.insert_instruction(("beqz","$"+loopCondReg[0],while_end,""))

        self.nearestLoopBegin.append(while_begin)
        self.nearestLoopEnd.append(while_end)
        WSTMT.loopBody.Perform_Operation(self)
        self.leave_tab()

        self.absmc.write("b %s\n"%(while_begin))
        self.insert_instruction(("b",while_begin,"",""))

        self.tab -=1

        self.absmc.write(""+while_end+":\t\t\t\t#End of while loop\n")
        self.insert_instruction((while_end,"","",""))

        self.nearestLoopBegin.pop()
        self.nearestLoopEnd.pop()
        
    def generate_FOR_STMT(self,FSTMT):
        for_begin = self.absmc.Generate_new_label()
        for_update = self.absmc.Generate_new_label()
        for_end = self.absmc.Generate_new_label()
        if(FSTMT.initExpr):
            FSTMT.initExpr.Perform_Operation(self)
        self.absmc.write(""+for_begin+":\t\t\t\t#Beginning of for loop\n")
        self.insert_instruction((for_begin,"","",""))

        self.tab += 1
        if(FSTMT.loopCond):
            loopCondReg = FSTMT.loopCond.Perform_Operation(self)
            self.leave_tab()
            self.absmc.write("beqz $%s, %s\n"%(loopCondReg[0],for_end))
            self.insert_instruction(("beqz","$"+loopCondReg[0],for_end,""))

        self.nearestLoopBegin.append(for_update)
        self.nearestLoopEnd.append(for_end)
        FSTMT.loopBody.Perform_Operation(self)
        if(FSTMT.updateExpr):
            self.absmc.write(""+for_update+":\t\t\t\t#update expression of for loop\n")
            self.insert_instruction((for_update,"","",""))

            FSTMT.updateExpr.Perform_Operation(self)
        self.leave_tab()
        self.absmc.write("b %s\n"%(for_begin))
        self.insert_instruction(("b",for_begin,"",""))

        self.tab -=1
        self.absmc.write(""+for_end+":\t\t\t\t#End of for loop\n")
        self.insert_instruction((for_end+":","","",""))

        self.nearestLoopBegin.pop()
        self.nearestLoopEnd.pop()

    def generate_RETURN_STMT(self,RSTMT):
        if(RSTMT.rValue):
            retReg = RSTMT.rValue.Perform_Operation(self)
            self.absmc.write("\n")
            self.leave_tab()
            self.absmc.write("move $v0, $%s   \t#save the return value\n"%retReg[0])
            self.insert_instruction(("move","$v0","$"+retReg[0],""))

            self.leave_tab()
            self.absmc.write("lw $ra, 28($sp) \t#restore the return address\n")
            self.insert_instruction(("lw","$ra","28($sp)",""))

            self.leave_tab()
            self.absmc.write("lw $fp, 24($sp) \t#restore the frame pointer\n")
            self.insert_instruction(("lw","$fp","24($sp)",""))

            self.leave_tab()
            self.absmc.write("addu $sp, $sp, 32 \t#restore the stack pointer\n")
            self.insert_instruction(("addu","$sp","$sp","32"))


            self.leave_tab()
            self.absmc.write("jr $ra\t\t\t\t#Return\n")
            self.insert_instruction(("jr","$ra","",""))
        else:
            self.absmc.write("\n")
            self.leave_tab()
            self.absmc.write("lw $ra, 28($sp) \t#restore the return address\n")
            self.insert_instruction(("lw","$ra","28($sp)",""))

            self.leave_tab()
            self.absmc.write("lw $fp, 24($sp) \t#restore the frame pointer\n")
            self.insert_instruction(("lw","$fp","24($sp)",""))

            self.leave_tab()
            self.absmc.write("addu $sp, $sp, 32 \t#restore the stack pointer\n")
            self.insert_instruction(("addu","$sp","$sp","32"))

            self.leave_tab()
            self.absmc.write("jr $ra\t\t\t\t#Return\n")
            self.insert_instruction(("jr","$ra","",""))

    def generate_BLOCK_STMT(self,BSTMT):

        if BSTMT.var is not None:
            for y in BSTMT.var:
                #if(y.kind == "formal" and y.addr == ""):

                if(y.kind == "local" and y.addr == ""):

                    if(y.typev == "int"):
                        y.addr = self.absmc.Generate_new_temporary()
                        self.absmc.write("\tli $%s, 0 # this holds %s\n"%(y.addr,y.name))
                        self.insert_instruction(("li","$"+y.addr,"0",""))

                    elif(y.typev == "float"):
                        y.addr = self.absmc.Generate_new_floating_temporary()
                        self.absmc.write("\tli.s $%s, 0.0 # this holds %s\n"%(y.addr,y.name))
                        self.insert_instruction(("li.s","$"+y.addr,"0.0",""))
                    else:
                        y.addr = self.absmc.Generate_new_temporary()
                        self.absmc.write("\tli $%s, 0 # this holds %s\n"%(y.addr,y.name))
                        self.insert_instruction(("li","$"+y.addr,"0",""))

        if BSTMT.body is not None:
            for y in BSTMT.body:
                y.Perform_Operation(self)

    def generate_BREAK_STMT(self,BRSTMT):
        if not self.nearestLoopEnd:
            print >> sys.stderr, "error : break without loop at lineno %s" %(BRSTMT.lineno[0])
            sys.exit()
        self.leave_tab()
        self.absmc.write("b "+self.nearestLoopEnd[-1]+"\t\t\t\t#This is the break\n")
        self.insert_instruction(("b",self.nearestLoopEnd[-1],"",""))

    def generate_CONTINUE_STMT(self,CSTMT):
        if not self.nearestLoopBegin:
            print >> sys.stderr, "error : continue without loop at lineno %s" %(CSTMT.lineno[0])
            sys.exit()
        self.leave_tab()
        self.absmc.write("b "+self.nearestLoopBegin[-1]+"\t\t\t\t#This is the continue\n")
        self.insert_instruction(("b",self.nearestLoopBegin[-1],"",""))

    def generate_SKIP_STMT(self,SSTMT):
        pass

    def generate_CONST_EXP(self,CEXP):

        self.leave_tab()
        new_loc = ""
        if(CEXP.exp_rtype == "int"):
            new_loc = self.absmc.Generate_new_temporary()
            self.absmc.write("li $%s, %s\n"%(new_loc,CEXP.value))
            self.insert_instruction(("li","$"+new_loc,str(CEXP.value),""))

        elif(CEXP.exp_rtype == "float"):
            new_loc = self.absmc.Generate_new_floating_temporary()
            self.absmc.write("li.s $%s, %s\n"%(new_loc,CEXP.value))
            self.insert_instruction(("li.s","$"+new_loc,CEXP.value,""))

        elif(CEXP.exp_rtype == "boolean"):
            new_loc = self.absmc.Generate_new_temporary()
            if(CEXP.value == "true"):
                self.absmc.write("li $%s, 1\n"%(new_loc))
                self.insert_instruction(("li","$"+new_loc,"1",""))

            if(CEXP.value == "false"):
                self.absmc.write("li $%s, 0\n"%(new_loc))
                self.insert_instruction(("li","$"+new_loc,"0",""))

        elif(CEXP.exp_rtype == "null"):
            new_loc = self.absmc.Generate_new_temporary()
            self.absmc.write("li $%s, -1\n"%(new_loc))
            self.insert_instruction(("li","$"+new_loc,"-1",""))

        return [new_loc,"reg","const"]
    
    def generate_VAR_EXP(self,VEXP):

        return [VEXP.var.addr,"reg","var_exp"]

    def generate_UNARY_EXP(self,UEXP):
        #Needs to be written for Boolean

        if(UEXP.Op == "uminus"):
            if(UEXP.exp_rtype == "int"):
                value_reg = self.absmc.Generate_new_temporary()

                loc1 = UEXP.exp.Perform_Operation(self)
                zero_reg = self.absmc.Generate_new_temporary()
                self.leave_tab()
                self.absmc.write("li $%s, %s\n"%(zero_reg,str(0)))
                self.insert_instruction(("li","$"+zero_reg,"0",""))

                self.leave_tab()
                self.absmc.write("sub $%s, $%s, $%s\n"%(value_reg,zero_reg,loc1[0]))
                self.insert_instruction(("sub","$"+value_reg,"$"+zero_reg,"$"+loc1[0]))

                return [value_reg,"reg","zero"]

            elif(UEXP.exp_rtype == "float"):
                value_reg = self.absmc.Generate_new_floating_temporary()
                loc1 = UEXP.exp.Perform_Operation(self)
                zero_reg = self.absmc.Generate_new_temporary()
                self.leave_tab()
                self.absmc.write("li.s $%s, %s\n"%(zero_reg,str(0.0)))
                self.insert_instruction(("li.s","$"+zero_reg,0.0))

                self.leave_tab()
                self.absmc.write("sub.s $%s, $%s, $%s\n"%(value_reg,zero_reg,loc1[0]))
                self.insert_instruction(("sub.s","$"+value_reg,"$"+zero_reg,"$"+loc1[0]))

                return [value_reg,"reg","zero"]

        elif(UEXP.Op == "neg"):
            if(UEXP.exp_rtype == "boolean"):

                value_reg = self.absmc.Generate_new_temporary()
                loc1 = UEXP.exp.Perform_Operation(self)
                one_reg = self.absmc.Generate_new_temporary()
                minus_reg = self.absmc.Generate_new_temporary()

                self.leave_tab()
                self.absmc.write("li $%s, %s\n"%(one_reg,str(1)))
                self.insert_instruction(("li","$"+one_reg,"1",""))

                self.leave_tab()
                self.absmc.write("li $%s, %s\n"%(minus_reg,str(-1)))
                self.insert_instruction(("li","$"+minus_reg,"-1",""))

                self.leave_tab()
                self.absmc.write("sub $%s, $%s, $%s\n"%(value_reg,loc1[0],one_reg))
                self.insert_instruction(("sub","$"+value_reg,"$"+loc1[0],"$"+one_reg))

                self.leave_tab()
                self.absmc.write("mul $%s, $%s, $%s\n"%(value_reg,value_reg,minus_reg))
                self.insert_instruction(("mul","$"+value_reg,"$"+value_reg,"$"+minus_reg))

                return [value_reg,"reg","zero"]

    def generate_BINARY_EXP(self,BEXP):

        loc1 = BEXP.exp1.Perform_Operation(self)
        loc2 = BEXP.exp2.Perform_Operation(self)
        new_rloc = self.absmc.Generate_new_temporary()

        self.leave_tab()

        if(self.Mapp.ioperatorMap[BEXP.Op] == "and"):

            self.leave_tab()
            self.absmc.write("mul $%s, $%s, $%s\n"%(new_rloc,loc1[0],loc2[0]))
            self.insert_instruction(("mul","$"+new_rloc,"$"+loc1[0],"$"+loc2[0]))

            return [new_rloc,"reg"]

        elif(self.Mapp.ioperatorMap[BEXP.Op] == "or"):

            self.leave_tab()
            self.absmc.write("add $%s, $%s, $%s\n"%(new_rloc,loc1[0],loc2[0]))
            self.insert_instruction(("add","$"+new_rloc,"$"+loc1[0],"$"+loc2[0]))
            return [new_rloc,"reg"]

        if(BEXP.exp1.exp_rtype == "int" and BEXP.exp2.exp_rtype == "int"):
            self.absmc.write("%s $%s, $%s, $%s\n"%
                         (self.Mapp.ioperatorMap[BEXP.Op],new_rloc,loc1[0],loc2[0]))
            self.insert_instruction((self.Mapp.ioperatorMap[BEXP.Op],"$"+new_rloc,"$"+loc1[0],"$"+loc2[0]))
        else:
            #float conversion
            if(BEXP.exp1.exp_rtype == "int" and BEXP.exp2.exp_rtype == "float"):
                new_reg = self.absmc.Generate_new_floating_temporary()
                self.absmc.write("mtc1 $%s, $%s\n"%(loc1[0],new_reg))
                self.leave_tab()
                self.absmc.write("cvt.s.w $%s, $%s\n"%(new_reg,new_reg))
                self.insert_instruction(("mtc1","$"+loc1[0],"$"+new_reg,""))
                self.insert_instruction(("cvt.s.w","$"+new_reg,"$"+new_reg,""))

                self.leave_tab()
                self.absmc.write("%s $%s, $%s, $%s\n"%
                             (self.Mapp.foperatorMap[BEXP.Op],new_rloc,new_reg,loc2[0]))
                self.insert_instruction((self.Mapp.foperatorMap[BEXP.Op],"$"+new_rloc,"$"+new_reg,"$"+loc2[0]))

            elif(BEXP.exp2.exp_rtype == "int" and BEXP.exp1.exp_rtype == "float" ):
                new_reg = self.absmc.Generate_new_floating_temporary()
                self.absmc.write("mtc1 $%s, $%s\n"%(loc2[0],new_reg))
                self.leave_tab()
                self.absmc.write("cvt.s.w $%s, $%s\n"%(new_reg,new_reg))
                self.insert_instruction(("mtc1","$"+loc2[0],"$"+new_reg,""))
                self.insert_instruction(("cvt.s.w","$"+new_reg,"$"+new_reg,""))

                self.leave_tab()
                self.absmc.write("%s $%s, $%s, $%s # floating\n"%
                             (self.Mapp.foperatorMap[BEXP.Op],new_rloc,loc1[0],new_reg))
                self.insert_instruction((
                    self.Mapp.foperatorMap[BEXP.Op],"$"+new_rloc,"$"+loc1[0],"$"+new_reg))
            else:
                self.absmc.write("%s $%s, $%s, $%s\n"%
                         (self.Mapp.ioperatorMap[BEXP.Op],new_rloc,loc1[0],loc2[0]))
                self.insert_instruction((
                    self.Mapp.foperatorMap[BEXP.Op],"$"+new_rloc,"$"+loc1[0],"$"+loc2[0]))

        return [new_rloc,"reg"]

    def generate_ASSIGN_EXP(self,AS_EXP):

        loc1 = AS_EXP.exp1.Perform_Operation(self)
        loc2 = AS_EXP.exp2.Perform_Operation(self)
        #Float conversion
        if(AS_EXP.exp1.exp_rtype == "float"
           and AS_EXP.exp2.exp_rtype == "int"):
            new_reg = self.absmc.Generate_new_floating_temporary()
            self.leave_tab()
            self.absmc.write("mtc1 $%s, $%s\n"%(loc2[0],new_reg))
            self.leave_tab()
            self.absmc.write("cvt.s.w $%s, $%s\n"%(new_reg,new_reg))
            self.insert_instruction(("mtc1","$"+loc2[0],"$"+new_reg,""))
            self.insert_instruction(("cvt.s.w","$"+new_reg,"$"+new_reg,""))
            loc2[0] = new_reg

        self.leave_tab()
        if(loc1[1] == "reg"):
            self.absmc.write("move $%s, $%s # Assign 1\n"%(loc1[0],loc2[0]))
            self.insert_instruction(("move","$"+loc1[0],"$"+loc2[0],""))

        else:
            #loc1[1] is the base
            #loc1[2] is the offset
            #loc2[0] is the value that is to stored
            addr = self.absmc.Generate_new_temporary()
            self.absmc.write("add $%s, $%s, $%s # address\n"%(addr,loc1[1],loc1[2]))
            self.insert_instruction(("add","$"+addr,"$"+loc1[1],"$"+loc1[2]))
            self.leave_tab()
            self.absmc.write("sw $%s ($%s) # base + offset value\n"%(loc2[0],addr))
            self.insert_instruction(("sw","$"+loc2[0],"($%s)"%(addr),""))
            #self.insert_instruction(("hstore",loc1[1],loc1[2],loc2[0]))
        return loc2

    def generate_AUTO_EXP(self,A_EXP):

        loc1     = A_EXP.exp.Perform_Operation(self)
        if(A_EXP.order == "pre"):
            if(A_EXP.Op == "increment"):
                if(A_EXP.exp.exp_rtype == "int"):

                    cont_1 = CONST_EXP("Integer_constant",1,(-1,-1),"int")
                    BIN_EXP = BINARY_EXP("+",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "int"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "int"
                    as_exp.rtype1 = "int"
                    as_exp.rtype2 = "int"
                    return as_exp.Perform_Operation(self)

                elif(A_EXP.exp.exp_rtype == "float"):
                    cont_1 = CONST_EXP("Float_constant",1.0,(-1,-1),"float")
                    BIN_EXP = BINARY_EXP("+",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "float"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "float"
                    as_exp.rtype1 = "float"
                    as_exp.rtype2 = "float"
                    return as_exp.Perform_Operation(self)

            elif(A_EXP.Op == "decrement"):
                if(A_EXP.exp.exp_rtype == "int"):

                    cont_1 = CONST_EXP("Integer_constant",1,(-1,-1),"int")
                    BIN_EXP = BINARY_EXP("-",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "int"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "int"
                    as_exp.rtype1 = "int"
                    as_exp.rtype2 = "int"
                    return as_exp.Perform_Operation(self)

                elif(A_EXP.exp.exp_rtype == "float"):

                    cont_1 = CONST_EXP("Float_constant",1.0,(-1,-1),"float")
                    BIN_EXP = BINARY_EXP("-",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "float"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "float"
                    as_exp.rtype1 = "float"
                    as_exp.rtype2 = "float"
                    return as_exp.Perform_Operation(self)

        elif(A_EXP.order == "post"):
            if(A_EXP.Op == "increment"):
                if(A_EXP.exp.exp_rtype == "int"):
                    pre_eval_reg = self.absmc.Generate_new_temporary()
                    self.leave_tab()
                    self.absmc.write("move $%s, $%s\n"%(pre_eval_reg,loc1[0]))
                    self.insert_instruction(("move","$"+pre_eval_reg,"$"+loc1[0],""))

                    cont_1 = CONST_EXP("Integer_constant",1,(-1,-1),"int")
                    BIN_EXP = BINARY_EXP("+",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "int"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "int"
                    as_exp.rtype1 = "int"
                    as_exp.rtype2 = "int"
                    as_exp.Perform_Operation(self)
                    return [pre_eval_reg,"reg"]

                elif(A_EXP.exp.exp_rtype == "float"):
                    pre_eval_reg = self.absmc.Generate_new_floating_temporary()
                    self.leave_tab()
                    self.absmc.write("move.s $%s, $%s\n"%(pre_eval_reg,loc1[0]))
                    self.insert_instruction(("move.s","$"+pre_eval_reg,"$"+loc1[0],""))

                    cont_1 = CONST_EXP("Float_constant",1.0,(-1,-1),"float")
                    BIN_EXP = BINARY_EXP("+",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "float"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "float"
                    as_exp.rtype1 = "float"
                    as_exp.rtype2 = "float"
                    as_exp.Perform_Operation(self)
                    return [pre_eval_reg,"reg"]

            if(A_EXP.Op == "decrement"):
                if(A_EXP.exp.exp_rtype == "int"):

                    pre_eval_reg = self.absmc.Generate_new_temporary()
                    self.leave_tab()
                    self.absmc.write("move $%s, $%s\n"%(pre_eval_reg,loc1[0]))
                    self.insert_instruction(("move ","$"+pre_eval_reg,"$"+loc1[0],""))

                    cont_1 = CONST_EXP("Integer_constant",1,(-1,-1),"int")
                    BIN_EXP = BINARY_EXP("-",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "int"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "int"
                    as_exp.rtype1 = "int"
                    as_exp.rtype2 = "int"
                    as_exp.Perform_Operation(self)
                    return [pre_eval_reg,"reg"]

                elif(A_EXP.exp.exp_rtype == "float"):
                    pre_eval_reg = self.absmc.Generate_new_floating_temporary()
                    self.leave_tab()
                    self.absmc.write("move.s $%s, $%s\n"%(pre_eval_reg,loc1[0]))
                    self.insert_instruction(("move.s","$"+pre_eval_reg,"$"+loc1[0],""))

                    cont_1 = CONST_EXP("Float_constant",1.0,(-1,-1),"float")
                    BIN_EXP = BINARY_EXP("-",A_EXP.exp,cont_1,(-1,-1))
                    BIN_EXP.exp_rtype = "float"
                    as_exp = ASSIGN_EXP(A_EXP.exp,BIN_EXP,(-1,-1))
                    as_exp.exp_rtype = "float"
                    as_exp.rtype1 = "float"
                    as_exp.rtype2 = "float"
                    as_exp.Perform_Operation(self)
                    return [pre_eval_reg,"reg"]

    def generate_FIELD_EXP(self,F_EXP):


        id_offset = self.Find_fieldOffset(F_EXP.resolvedID)
        offset    = self.absmc.Generate_new_temporary()
        exp_reg   = F_EXP.exp.Perform_Operation(self)

        self.leave_tab()
        self.absmc.write("li $%s, %s # Field Offset\n"%(offset,str(id_offset)))
        self.insert_instruction(("li","$"+offset,str(id_offset),""))
        self.leave_tab()
        if(F_EXP.exp_rtype == "float"):
            tar_reg   = self.absmc.Generate_new_floating_temporary()
            addr = self.absmc.Generate_new_temporary()
            if(exp_reg[0] == "sap"):
                exp_reg[0] = self.absmc.Generate_new_temporary()
                self.absmc.write("la $%s, sap\t#load the address of sap\n"%(exp_reg[0]))
                self.insert_instruction(("la","$"+exp_reg[0],"sap",""))
                self.leave_tab()
            self.absmc.write("add $%s, $%s, $%s\n"%(addr,exp_reg[0],offset))
            self.insert_instruction(("add","$"+addr,"$"+exp_reg[0],"$"+offset))
            self.leave_tab()
            self.absmc.write("lw.s $%s, ($%s) # loading the value of field\n"%(tar_reg,addr))
            self.insert_instruction(("lw.s","$"+tar_reg,"($%s)"%addr,""))
            #tar_reg contains the R-Value
            #exp_reg and offset is the L-Value of the register
            return [tar_reg,exp_reg[0],offset]

        else:
            tar_reg   = self.absmc.Generate_new_temporary()
            addr = self.absmc.Generate_new_temporary()
            if(exp_reg[0] == "sap"):
                exp_reg[0] = self.absmc.Generate_new_temporary()
                self.absmc.write("la $%s, sap\t#load the address of sap\n"%(exp_reg[0]))
                self.insert_instruction(("la","$"+exp_reg[0],"sap",""))
                self.leave_tab()
            self.absmc.write("add $%s, $%s, $%s\n"%(addr,exp_reg[0],offset))
            self.leave_tab()
            self.absmc.write("lw $%s, ($%s)\t#loading the value of field\n"%(tar_reg,addr))
            self.insert_instruction(("add","$"+addr,"$"+exp_reg[0],"$"+offset))
            self.insert_instruction(("lw","$"+tar_reg,"($%s)"%addr,""))
            #tar_reg contains the R-Value
            #exp_reg and offset is the L-Value of the register
            return [tar_reg,exp_reg[0],offset]


    def generate_METHOD_CALL_EXP(self,MC_EXP):
        #value of object whose method is being accessed
        obj_val = MC_EXP.exp.Perform_Operation(self)
        fcounter = 0
        #Code to take care of the float registers
        if(self.absmc.fregister > 0):
            self.leave_tab()
            self.absmc.write("move $s0, $a0 \t#save $a0\n")
            self.insert_instruction(("move","$s0","$a0",""))

            self.leave_tab()
            self.absmc.write("li $v0, 9     \t#Allocate memory\n")
            self.insert_instruction(("li","$v0","9",""))

            self.leave_tab()
            self.absmc.write("li $a0, 128    \t#we need this much memory\n")
            self.insert_instruction(("li","$a0","128",""))

            self.leave_tab()
            self.absmc.write("syscall       \t#make the call to get memory\n")
            self.insert_instruction(("syscall","","",""))

            self.leave_tab()
            self.absmc.write("move $s2, $v0 \tsave the memory address in $s2\n")
            self.insert_instruction(("move","$s1","$v0",""))

            self.leave_tab()
            self.absmc.write("move $a0, $s0 \t#restoring $a0\n")
            self.insert_instruction(("move","$a0","$s0",""))

            self.absmc.write("\n")
            fcounter = 0
            for j in range(0,self.absmc.fregister):
                self.leave_tab()
                self.absmc.write("sw.s $f%s, %s($s2)\t#save float register\n"%(str(j),str(fcounter)))
                self.insert_instruction(("sw.s","$f%s"%str(j),"%s($s2)"%(str(fcounter)),""))
                fcounter = fcounter + 4

        self.leave_tab()
        self.absmc.write("move $s0, $a0 \t#save $a0\n")
        self.insert_instruction(("move","$s0","$a0",""))

        self.leave_tab()
        self.absmc.write("li $v0, 9     \t#Allocate memory\n")
        self.insert_instruction(("li","$v0","9",""))

        self.leave_tab()
        self.absmc.write("li $a0, 128    \t#we need this much memory\n")
        self.insert_instruction(("li","$a0","128",""))

        self.leave_tab()
        self.absmc.write("syscall       \t#make the call to get memory\n")
        self.insert_instruction(("syscall","","",""))

        self.leave_tab()
        self.absmc.write("move $s1, $v0 \tsave the memory address in $s1\n")
        self.insert_instruction(("move","$s1","$v0",""))

        self.leave_tab()
        self.absmc.write("move $a0, $s0 \t#restoring $a0\n")
        self.insert_instruction(("move","$a0","$s0",""))

        self.absmc.write("\n")
        counter = 0
        for i in range(0,self.absmc.arg):
            self.leave_tab()
            self.absmc.write("sw $a%s, %s($s1)\t#save \n"%(str(i),str(counter)))
            self.insert_instruction(("sw","$a%s"%str(i),"%s($s1)"%(str(counter)),""))
            counter = counter + 4

        for j in range(0,self.absmc.register):
            self.leave_tab()
            self.absmc.write("sw $t%s, %s($s1)\t#save\n"%(str(j),str(counter)))
            self.insert_instruction(("sw","$t%s"%str(j),"%s($s1)"%(str(counter)),""))
            counter = counter + 4

        arg_val = self.absmc.arg        #Number of register allocated till far
        temp_val = self.absmc.register  #Number of temporary register allocated till far
        ftemp_val = self.absmc.fregister #Number of float regiter allocated till far

        self.leave_tab()
        #now moving arguments of method on args register
        #Static method call checking
        if(obj_val[0] != "sap"):
            self.leave_tab()
            self.absmc.write("move $a0, $%s\n"%(obj_val[0]))
            self.insert_instruction(("move","$a0","$"+obj_val[0],""))
            self.absmc.arg = 1
        else:
            self.absmc.arg = 0

        self.absmc.register = 0
        self.absmc.fregister  = 0
        addr = 20
        #moving arguments of method on args register
        if(MC_EXP.arguments is not None):
            for x in MC_EXP.arguments:
                reg = x.Perform_Operation(self)[0]

                if(self.absmc.arg < 4):
                    arg_reg = self.absmc.alloc_argument_register()
                    self.leave_tab()
                    self.absmc.write("move $%s, $%s\n"%(arg_reg, reg))
                    self.insert_instruction(("move","$"+arg_reg,"$"+reg,""))
                else:
                    self.leave_tab()
                    self.absmc.write("sw $%s, %s($sp)\n"%(reg,str(addr)))
                    self.insert_instruction(("sw","$%s"%reg,"%s($sp)"%str(addr),""))
                    addr -= 4

        self.leave_tab()
        self.absmc.write("jal M_%s_%s\n"%(MC_EXP.name,MC_EXP.resolveID))
        self.insert_instruction((("jal M_%s_%s"
                                  %(MC_EXP.name,MC_EXP.resolveID)),"","",""))

        self.absmc.write("")
        #restoring the earlier value again
        counter = counter - 4
        for i in range(temp_val-1,-1,-1):
            self.leave_tab()
            self.absmc.write("lw $t%s, %s($s1)\t#restore \n"%(i,str(counter)))
            self.insert_instruction(("lw","$t%s"%(i),"%s($s1)"%(str(counter)),""))
            counter -= 4
        if(self.absmc.fregister > 0):
            fcounter = fcounter - 4
            for i in range(ftemp_val-1,-1,-1):
                self.leave_tab()
                self.absmc.write("lw.s $f%s, %s($s2)\t#restore the float register\n"%(i,str(fcounter)))
                self.insert_instruction(("lw.s","$f%s"%(i),"%s($s2)"%(str(fcounter)),""))
                fcounter -= 4

        self.absmc.register = temp_val
        self.absmc.fregister = ftemp_val

        ret_val = self.absmc.Generate_new_temporary()
        self.leave_tab()
        self.absmc.write("move $%s, $v0\t#saving the return val\n"%(ret_val))
        self.insert_instruction(("move","$"+ret_val,"a0",""))

        for i in range(arg_val-1,-1,-1):
            self.leave_tab()
            self.absmc.write("lw $a%s, %s($s1)\t#restore \n"%(i,str(counter)))
            self.insert_instruction(("lw","a%s"%(i),"%s($s1)"%(str(counter)),""))
            counter -= 4

        self.absmc.write("\n")
        self.absmc.arg = arg_val
        return [ret_val,"reg"]

    def generate_NEW_OBJ_EXP(self,NO_EXP):

        new_reg = self.absmc.Generate_new_temporary()
        space_reg = self.absmc.Generate_new_temporary()
        fcounter = 0
        #Code to take care of the float registers
        if(self.absmc.fregister > 0):
            self.leave_tab()
            self.absmc.write("move $s0, $a0 \t#save $a0\n")
            self.insert_instruction(("move","$s0","$a0",""))

            self.leave_tab()
            self.absmc.write("li $v0, 9     \t#Allocate memory\n")
            self.insert_instruction(("li","$v0","9",""))

            self.leave_tab()
            self.absmc.write("li $a0, 128    \t#we need this much memory\n")
            self.insert_instruction(("li","$a0","128",""))

            self.leave_tab()
            self.absmc.write("syscall       \t#make the call to get memory\n")
            self.insert_instruction(("syscall","","",""))

            self.leave_tab()
            self.absmc.write("move $s2, $v0 \tsave the memory address in $s2\n")
            self.insert_instruction(("move","$s1","$v0",""))

            self.leave_tab()
            self.absmc.write("move $a0, $s0 \t#restoring $a0\n")
            self.insert_instruction(("move","$a0","$s0",""))

            self.absmc.write("\n")
            fcounter = 0
            for j in range(0,self.absmc.fregister):
                self.leave_tab()
                self.absmc.write("sw.s $f%s, %s($s2)\t#save\n"%(str(j),str(fcounter)))
                self.insert_instruction(("sw.s","$f%s"%str(j),"%s($s2)"%(str(fcounter)),""))
                fcounter = fcounter + 4

        self.absmc.write("              \t#Allocation starts for object\n")
        self.leave_tab()
        self.absmc.write("li $%s, %s    \t#space required for allocation\n"
                         %(space_reg,str(self.ClassMemInfo[NO_EXP.cname])))
        self.insert_instruction(("li","$"+space_reg,str(self.ClassMemInfo[NO_EXP.cname]),""))

        self.leave_tab()
        self.absmc.write("move $s0, $a0 \t#save $a0\n")
        self.insert_instruction(("move","$s0","$a0",""))

        self.leave_tab()
        self.absmc.write("li $v0, 9     \t#Allocate memory\n")
        self.insert_instruction(("li","$v0","9",""))

        self.leave_tab()
        self.absmc.write("move $a0, $%s \t#we need this much memory for %s\n"%(space_reg,NO_EXP.cname))
        self.insert_instruction(("move","$a0","$"+space_reg,""))

        self.leave_tab()
        self.absmc.write("syscall       \t#make the call to get memory\n")
        self.insert_instruction(("syscall","","",""))

        self.leave_tab()
        self.absmc.write("move $%s, $v0 \t#save the memory address\n"%(new_reg))
        self.insert_instruction(("move","$"+new_reg,"$v0",""))

        self.leave_tab()
        self.absmc.write("move $a0, $s0 \t#restoring $a0\n")
        self.insert_instruction(("move","$a0","$s0",""))

        self.absmc.write("              \t#Allocation process ends\n")
        self.absmc.write("\n")

        self.leave_tab()
        self.absmc.write("move $s0, $a0 \t#save $a0\n")
        self.insert_instruction(("move","$s0","$a0",""))

        self.leave_tab()
        self.absmc.write("li $v0, 9     \t#Allocate memory\n")
        self.insert_instruction(("li","$v0","9",""))

        self.leave_tab()
        self.absmc.write("li $a0, 128    \t#we need this much memory\n")
        self.insert_instruction(("li","$a0","128",""))

        self.leave_tab()
        self.absmc.write("syscall       \t#make the call to get memory\n")
        self.insert_instruction(("syscall","","",""))

        self.leave_tab()
        self.absmc.write("move $s1, $v0 \tsave the memory address in $s1\n")
        self.insert_instruction(("move","$s1","$v0",""))

        self.leave_tab()
        self.absmc.write("move $a0, $s0 \t#restoring $a0\n")
        self.insert_instruction(("move","$a0","$s0",""))

        self.absmc.write("\n")

        # self.leave_tab()
        # self.absmc.write("halloc %s, %s #Allocate for %s\n"
        #              %(new_reg,space_reg,NO_EXP.cname))
        #
        # self.insert_instruction(("halloc",new_reg,space_reg,NO_EXP.cname))
        counter = 0
        for i in range(0,self.absmc.arg):
            self.leave_tab()
            self.absmc.write("sw $a%s, %s($s1)\t#save \n"%(str(i),str(counter)))
            self.insert_instruction(("sw","$a%s"%str(i),"%s($s1)"%(str(counter)),""))
            counter = counter + 4

        for j in range(0,self.absmc.register):
            self.leave_tab()
            self.absmc.write("sw $t%s, %s($s1)\t#save\n"%(str(j),str(counter)))
            self.insert_instruction(("sw","$t%s"%str(j),"%s($s1)"%(str(counter)),""))
            counter = counter + 4

        arg_val = self.absmc.arg        #Number of register allocated till far
        temp_val = self.absmc.register  #Number of temporary register allocated till far
        ftemp_val = self.absmc.fregister #Number of floating register allocated till far
        #First argument will be reference
        self.leave_tab()
        self.absmc.write("move $a0, $%s #moving the reference\n"%(new_reg))
        self.insert_instruction(("move","$a0","$"+new_reg,""))

        self.absmc.arg = 1
        self.absmc.register = 0
        self.absmc.fregister  = 0

        if(NO_EXP.arguments is not None):
            for x in NO_EXP.arguments:
                self.leave_tab()
                self.absmc.write("move $%s, $%s\n"%(self.absmc.alloc_argument_register(),
                             x.Perform_Operation(self)[0]))
                self.insert_instruction(("move","$"+self.absmc.alloc_argument_register(),
                                         "$"+x.Perform_Operation(self)[0],""))
        self.leave_tab()
        self.absmc.write("jal C_%s\n"%(NO_EXP.resolveID))
        self.insert_instruction(("jal C_%s"%(NO_EXP.resolveID),"","",""))
        #restoring the earlier value again
        counter = counter - 4
        for i in range(temp_val-1,-1,-1):
            self.leave_tab()
            self.absmc.write("lw $t%s, %s($s1)\t#restore\n"%(i,str(counter)))
            self.insert_instruction(("lw","$t%s"%(i),"%s($s1)"%(str(counter)),""))
            counter = counter - 4
        self.absmc.register = temp_val

        if(self.absmc.fregister > 0):
            fcounter = fcounter - 4
            for i in range(temp_val-1,-1,-1):
                self.leave_tab()
                self.absmc.write("lw.s $f%s, %s($s2)\t#restore the floating register\n"%(i,str(fcounter)))
                self.insert_instruction(("lw.s","$f%s"%(i),"%s($s2)"%(str(fcounter)),""))
                fcounter = fcounter - 4
            self.absmc.fregister = ftemp_val

        for i in range(arg_val-1,-1,-1):
            self.leave_tab()
            self.absmc.write("lw $a%s, %s($s1)\t#restore\n"%(i,str(counter)))
            self.insert_instruction(("restore","$a%s"%(i),"%s($s1)"%(str(counter)),""))
            counter = counter - 4
        self.absmc.arg = arg_val
        #No R-value only L-Value
        return [new_reg,"reg"] # Constructor doesn't returns anything

    def generate_THIS_EXP(self,TH_EXP):
        return ["a0","reg","this"]

    def generate_SUPER_EXP(self,SU_EXP):
        return ["a0","reg","super"]

    def generate_CLASS_REF_EXP(self,CR_EXP):
        return ["sap","reg","classref"]

    def generate_ARR_ACC_EXP(self,AA_EXP):

        base_exp = AA_EXP.exp1.Perform_Operation(self)
        index_exp = AA_EXP.exp2.Perform_Operation(self)
        addr  =self.absmc.Generate_new_temporary()
        tar_reg = self.absmc.Generate_new_temporary()
        self.leave_tab()

        # self.absmc.write("hload %s, %s, %s #load array value from heap\n"
        #              %(tar_reg,base_exp[0],index_exp[0]))
        # self.insert_instruction(("hload",tar_reg,base_exp[0],index_exp[0]))

        self.absmc.write("add $%s, $%s, $%s\t\t#adding base+offset\n"
                         %(addr,base_exp[0],index_exp[0]))
        self.insert_instruction(("add","$"+addr,"$"+base_exp[0],"$"+index_exp[0]))

        self.leave_tab()
        self.absmc.write("lw $%s, ($%s)\t\t#load value\n"%(tar_reg,addr))
        self.insert_instruction(("lw","$"+tar_reg,"($%s)"%addr))
        return [tar_reg, base_exp[0], index_exp[0]]

    def generate_NEW_ARR_EXP(self,NA_EXP):
        #NA_EXP.basetype
        #NA_EXP.dimension
        tot_dem_reg = self.absmc.Generate_new_temporary()
        self.leave_tab()
        self.absmc.write("li $%s, %s # This reg will contain total dimension\n"
                     %(tot_dem_reg,str(1)))
        self.insert_instruction(("li","$"+tot_dem_reg,"1",""))

        if(NA_EXP.dimension is not None):
            dim = None
            for dimension in NA_EXP.dimension:
                dim = dimension.Perform_Operation(self)[0]
                self.leave_tab()
                self.absmc.write("mul $%s, $%s, $%s # multiplying to get dimension\n" %
                             (tot_dem_reg,tot_dem_reg,
                              dim))
            self.insert_instruction(("mul","$"+tot_dem_reg,"$"+tot_dem_reg, "$"+dim))

        self.leave_tab()
        ref_reg = self.absmc.Generate_new_temporary()

        self.absmc.write("\n")


        self.absmc.write("             \t#allocation process starts\n")

        self.leave_tab()
        self.absmc.write("move $s0, $a0\n")
        self.insert_instruction(("move","$s0","$a0",""))

        self.leave_tab()
        self.absmc.write("li $v0, 9   \t#Allocate memory\n")
        self.insert_instruction(("li","$v0","9",""))

        self.leave_tab()
        self.absmc.write("move $a0, $%s\t#Total dimension\n"%(tot_dem_reg))
        self.insert_instruction(("move","$a0","$"+tot_dem_reg,""))

        self.leave_tab()
        self.absmc.write("syscall      \t#call to allocated memory\n")
        self.insert_instruction(("syscall","","",""))

        self.leave_tab()
        self.absmc.write("move $%s, $v0\t#moving the reference to memory\n"%(ref_reg))
        self.insert_instruction(("move","$%s"%(ref_reg),"$v0",""))

        self.leave_tab()
        self.absmc.write("move $a0, $s0\t#restoring $a0\n")
        self.insert_instruction(("move","$a0","$s0",""))
        self.absmc.write("             \t#allocation process ends\n")
        # self.absmc.write("halloc %s, %s # allocate space for array\n"
        #              %(ref_reg,tot_dem_reg))
        # self.insert_instruction(("halloc",ref_reg,tot_dem_reg,""))

        return [ref_reg,"reg"]

    def Find_fieldOffset(self,resolveID):

        for CLASS in self.AST_TABLE.children:
            for field in CLASS.Fields:
                if(field.id == resolveID):
                    return field.offset

class CodeGen(object):

    def __init__(self,subtype_tuple,AST_TABLE,fileName):
        self.subtype_tuple = subtype_tuple
        self.ClassMemInfo = {}
        self.AST_TABLE = AST_TABLE
        self.InstructionSet = []
        self.Generate_Code(fileName)
        self.Generate_SSA(self.InstructionSet,fileName)
        self.static = -1
    def Generate_Code(self,fileName):

        generator = Code_Generator(self.AST_TABLE,fileName)
        for CLASS in self.AST_TABLE.children:
            CLASS.Perform_Operation(generator)
        generator.absmc.write(".data \n")
        generator.insert_instruction((".data","","",""))
        self.static = generator.static

        mem = 32*generator.static
        generator.absmc.write("sap: .space %s\n"%(str(mem)))
        generator.insert_instruction(("sap:",".space",str(mem),""))

        generator.absmc.write(".text\n")

        for CLASS in self.AST_TABLE.children:

            for CONSTRUCTORS in CLASS.CConstructors:
                CONSTRUCTORS.Perform_Operation(generator)

            for METHODS in CLASS.Methods :
                METHODS.Perform_Operation(generator)
# 
#             print "Field offset for %s"%(CLASS.name)
#             for FIELD in CLASS.Fields:
#                 print FIELD.offset
#        generator.printDict()
        self.InstructionSet = generator.InstructionSet

    def Generate_SSA(self,InstructionSet,filename):
        ssa_util = SSA_UTIL()
        fileName = open(filename.split(".")[0]+".asm",'w')

        fileName.write(".data \n")
        mem = 32*self.static
        fileName.write("sap: .space %s\n"%(str(mem)))
        fileName.write(".text\n")
        ssa_construction = SSA_CONSTRUCTION(ssa_util,fileName)

        for Index in InstructionSet:
            if(InstructionSet[Index].irnode[0][0:2] == "M_" or
                       InstructionSet[Index].irnode[0][0:2] == "C_"or
                        InstructionSet[Index].irnode[0][0:4] == "main"):
                ssa_util.ProcedureIndex = ssa_util.ProcedureIndex + [Index]

        Counter = 0
        length = len(ssa_util.ProcedureIndex)
        for element in ssa_util.ProcedureIndex:
            if((Counter + 1) < length and
                           element + 1 != ssa_util.ProcedureIndex[Counter + 1] ):
                ssa_construction.Perform_Optimization(element,
                                                       ssa_util.ProcedureIndex[Counter+1],
                                                      InstructionSet)
            Counter = Counter + 1

        #Last Block
        ssa_construction.Perform_Optimization(ssa_util.ProcedureIndex[Counter-1],
                                              len(InstructionSet),InstructionSet)
