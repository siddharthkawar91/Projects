# Parser
import re
import sys
import ply.yacc as yacc
from AST import *


# class for Parsing DECAFE


class DECAFPARSER(object):
    parseSuccess = True

    # Passing the lexer tokens
    def __init__(self, token):
        self.tokens = token
        self.parser = yacc.yacc(module=self)
        self.CLASS_TABLE = CLASS_TABLE("CLASS_TABLE")  # This is the core of AST
        self.stack = []  # Scope stack. Top entry on the stack indicates current scope
        self.buildStdClasses()
        self.CLASS_NAME = ["In","Out"]
    def buildStdClasses(self):
        In = CLASS("In", "", [[METHOD("scan_int", ["public", "static"], [], None, "int",(0,0)),
                               METHOD("scan_float", ["public", "static"], [], None, "float",(0,0))]])

        Out = CLASS("Out", "", [[METHOD("print", ["public", "static"], [VARIABLE("i", "int", "formal")], None,"void",(0,0)),
                                 METHOD("print", ["public", "static"], [VARIABLE("f", "float", "formal")], None,"void",(0,0)),
                                 METHOD("print", ["public", "static"], [VARIABLE("b", "boolean", "formal")], None,"void",(0,0)),
                                 METHOD("print", ["public", "static"], [VARIABLE("s", "string", "formal")], None,"void",(0,0))]])

        self.CLASS_TABLE.Insert(In)
        self.CLASS_TABLE.Insert(Out)

    def p_program(self, p):
        '''program :  class_decl program
					| empty
					'''

    # program might be empty



    def p_class_decl(self, p):
        '''class_decl : CLASS class_id EXTENDS ID class_body
					  | CLASS class_id class_body'''
        # CP[]lass decalartion
        if(self.parseSuccess == True):
            if (len(p) > 4):
                p[0] = CLASS(p[2], p[4], p[5])
                self.CLASS_TABLE.Insert(p[0])
            else:
                p[0] = CLASS(p[2], "", p[3])  # No super class
                self.CLASS_TABLE.Insert(p[0])

        # self.CLASS_TABLE.PRINT()
        # self.CLASS_TABLE.LookUp()

    def p_class_id(self, p):
        '''class_id : ID'''
        if (self.CLASS_TABLE.Lookup(p[1]) == True):
            print >> sys.stderr, "error : redeclaration of class %s at line %d " % (p[1], p.lineno(1))
            sys.exit()
        else:
            p[0] = p[1]
            self.CLASS_NAME = self.CLASS_NAME + [p[1]]

    def p_class_body(self, p):
        '''class_body : LBRACE class_body_declaration1 RBRACE'''
        p[0] = p[2]
    def p_class_body_error(self,p):
        '''class_body : LBRACE class_body_declaration1 error RBRACE'''
        pass

    def p_class_body_declaration1(self, p):
        '''class_body_declaration1 : class_body_declaration inter_class_body_declaration '''

        if p[2] is not None:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_inter_class_body_declaration(self, p):
        ''' inter_class_body_declaration : class_body_declaration inter_class_body_declaration
										 | empty'''
        # class body decalaration goes to one or more class body decalaration
        if p[1] is not None:
            if (p[2] is not None):
                p[0] = p[1] + p[2]
            else:
                p[0] = p[1]

    def p_class_body_declaration(self, p):
        ''' class_body_declaration : field_decl
								   | method_decl
								   | constructor_decl'''

        p[0] = [p[1]]

    def p_constructor_decl(self, p):
        ''' constructor_decl : modifier ID LEFTPr rightpr block
							 | modifier ID LEFTPr formals rightpr block'''
        if (len(p) == 6):
            p[0] = CONSTRUCTOR(p[2], p[1][0], [], p[5], (p.lineno(2),p.lineno(5)))
        else:
            p[0] = CONSTRUCTOR(p[2],p[1][0], p[4], p[6],(p.lineno(2),p.lineno(6)))
        p[0] = [p[0]]

    def p_method_decl(self, p):
        ''' method_decl : modifier type ID LEFTPr formals rightpr block
						| modifier type ID LEFTPr rightpr block
						| modifier VOID ID LEFTPr formals rightpr block
						| modifier VOID ID LEFTPr rightpr block'''
        if (len(p) == 8):
            p[0] = METHOD(p[3], p[1], p[5], p[7], p[2],(p.lineno(3),p.lineno(7)))
        else:
            p[0] = METHOD(p[3], p[1], [], p[6], p[2],(p.lineno(3),p.lineno(6)))
        p[0] = [p[0]]

    def p_rightpr(self, p):
        '''rightpr : RIGHTPr'''
        if (p[-1] == '('):          #if formals is none then just append empty list
            self.stack.append([])
        else:                       #if formals is not none then append all the parameter on the scope stack
            self.stack.append([])
            self.stack[len(self.stack) - 1] = self.stack[len(self.stack) - 1] + p[-1]
        p[0] = "formals"

    def p_formals(self, p):
        ''' formals : formals_param inter_formals'''
        if p[2] is not None:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_inter_formals(self, p):
        ''' inter_formals : COMMA formals_param inter_formals
						  | empty'''

        if p[1] is not None:
            if p[3] is not None:
                p[0] = p[2] + p[3]
            else:
                p[0] = p[2]

    def p_formals_param(self, p):
        ''' formals_param : type variable'''
        p[2][0].kind = "formal"
        p[0] = p[2]

    def p_field_decl(self, p):
        ''' field_decl : modifier var_decl'''

        if (p[1] is not None):
            p[0] = MFIELDS(p[2], p[1], (p.lineno(2),p.lineno(2))).Field
        else:
            p[0] = MFIELDS(p[2],None,(p.lineno(2),p.lineno(2))).Field

    def p_modifier(self, p):
        ''' modifier : visibility_mod storage_mod'''
        if p[1] is not None:
            p[0] = p[1] + p[2]

    def p_storage_mod(self, p):
        ''' storage_mod : STATIC
        				| empty'''
        if(p[1] is not None):
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_visibility_mod(self, p):
        ''' visibility_mod  : PUBLIC
							| PRIVATE
						    | empty'''
        if(p[1] is not None):
            p[0] = p[1]
        else:
            p[0] = "private"
        p[0] = [p[0]]
    def p_var_decl(self, p):
        ''' var_decl : type variables SEMIC'''
        p[0] = p[2]
        p.set_lineno(0, p.lineno(3))

    def p_type(self, p):
        ''' type     : INT
					 | BOOLEAN
					 | FLOAT
					 | userid'''
        p[0] = p[1]

    def p_userid(self, p):
        '''userid : ID'''
        p[0] = "User(" + p[1] + ")"

    def p_variables(self, p):
        '''variables : variable inter_variables'''
        if p[2] is not None:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_inter_variables(self, p):
        '''inter_variables : comma variable inter_variables
						   | empty'''
        if p[1] is not None:
            if p[3] is not None:
                p[0] = p[2] + p[3]
            else:
                p[0] = p[2]

    def p_comma(self, p):
        '''comma : COMMA'''   #Because we have list and there is only one element in it

        if(p[-1][0].typev[:6] == "array(" ):
            rtype = p[-1][0].typev
            p[0] = self.Extracttype(rtype)
        else:
            p[0] = p[-1][0].typev

    def Extracttype(self,rtype):
        if(rtype[:6] == "array("):
            rtype = rtype[6:-1]
            return self.Extracttype(rtype)
        else:
            return rtype

    def p_variable(self, p):
        '''variable : ID arr'''
        if p[2] is not None:
            p[0] = [VARIABLE(p[1], p[2], "local")]
        else:
            p[0] = [VARIABLE(p[1], p[-1], "local")]

    def p_arr(self, p):
        ''' arr : leftBr RIGHTBr arr
				| empty'''
        if (p[1] is not None):
            if (p[3] is not None):
                p[0] = "array(" + p[3] + ")"

            else:
                p[0] = "array(" + p[1] + ")"

    def p_leftBr(self, p):
        '''leftBr : LEFTBr'''
        p[0] = p[-2]

    def p_block(self, p):
        ''' block : lbrace inter_stmt rbrace'''
        # stmt can be empty
        # p[3] contains the list of all variable accessible in this particular block
        # p[2] contains the list of statements
        p.set_lineno(0, p.lineno(3))
        if (p[2] is not None):
           p[0] = BLOCK_STMT(p[3], p[2], (p.lineno(1), p.lineno(3)))
        else:
           p[0] = BLOCK_STMT(p[3], [], (p.lineno(1), p.lineno(3)))

        p.set_lineno(0, p.lineno(3))

    def p_block_error(self,p):
        '''block : lbrace inter_stmt error rbrace'''

    def p_lbrace(self, p):
        ''' lbrace : LBRACE '''
        if (p[-1] != "formals"): #if block doesn't succeed formals
            self.stack.append([])
        else:
            p[-1] = ")"
        p.set_lineno(0, p.lineno(1))

    def p_rbrace(self, p):
        ''' rbrace : RBRACE'''
        blockVars = []
        for var in self.stack:
            for ivar in var:
                blockVars.append(ivar)

        self.stack.pop()
        p[0] = blockVars
        p.set_lineno(0, p.lineno(1))

    def p_inter_stmt(self, p):
        ''' inter_stmt : inter_stmt stmt'''

        if (p[1] is not None):
           if p[2] == "var_decl":
                p[0] = p[1]
           else:
               p[0] = p[1] + [p[2]]
        else:
            if p[2] == "var_decl":
               p[0] = []
            else:
               p[0] = [p[2]]

    def p_inter_stmt_empty(self,p):
        '''inter_stmt : empty'''

    def p_stmt_1(self, p):
        ''' stmt : IF LEFTPr expr RIGHTPr stmt %prec IFX'''
        # giving ELSE statement more priority to avoid dangling if else problem
        # p[0] = p[1] + p[2] + p[3] + p[4] + p[5]
        p[0] = IF_STMT(p[3], p[5], (p.lineno(1), p.lineno(5)))
        p.set_lineno(0, p.lineno(5))

    def p_stmt_2(self, p):
        ''' stmt : IF LEFTPr expr RIGHTPr stmt ELSE stmt'''
        # p[0] = p[1] +p[2] + p[3] +p[4] + p[5] + p[6] + p[7]
        p[0] = IF_STMT(p[3], p[5], (p.lineno(1), p.lineno(7)), p[7])
        p.set_lineno(0, p.lineno(7))

    def p_stmt_3(self, p):
        ''' stmt :  WHILE LEFTPr expr RIGHTPr stmt'''
        # p[0] = p[1] + p[2] + p[3] + p[4] + p[5]
        p[0] = WHILE_STMT(p[3], p[5], (p.lineno(1), p.lineno(5)))
        p.set_lineno(0, p.lineno(5))

    def p_stmt_4(self, p):
        ''' stmt : FOR LEFTPr se SEMIC e SEMIC se RIGHTPr stmt'''
        # p[0] = p[1] + p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9]
        p[0] = FOR_STMT(p[3], p[5], p[7], p[9], (p.lineno(1), p.lineno(9)))
        p.set_lineno(0, p.lineno(9))

    def p_stmt_5(self, p):
        ''' stmt : RETURN e SEMIC'''
        p[0] = RETURN_STMT(p[2], (p.lineno(1), p.lineno(3)))
        p.set_lineno(0, p.lineno(3))

    def p_stmt_6(self, p):
        ''' stmt : stmt_expr SEMIC'''
        p[0] = p[1]
        p.set_lineno(0, p.lineno(2))

    def p_stmt_7(self, p):
        ''' stmt : BREAK SEMIC'''
        p[0] = BREAK_STMT((p.lineno(1), p.lineno(2)))
        p.set_lineno(0, p.lineno(2))

    def p_stmt_8(self, p):
        ''' stmt : CONTINUE SEMIC'''
        p[0] = CONTINUE_STMT((p.lineno(1), p.lineno(2)))
        p.set_lineno(0, p.lineno(2))

    def p_stmt_9(self, p):
        '''stmt : block'''
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_stmt_10(self, p):
        '''stmt : var_decl'''
        err = ""
        for var in p[1]:
            for ivar in self.stack[len(self.stack) - 1]:
                if (var.name == ivar.name):
                    print >> sys.stderr, "error : redeclaration of variable %s at line %d !!!" % (var.name, p.lineno(1))
                    sys.exit()

        self.stack[len(self.stack) - 1] = self.stack[len(self.stack) - 1] + p[1]
        p[0] = "var_decl"
        p.set_lineno(0, p.lineno(1))

    def p_stmt_11(self, p):
        ''' stmt : SEMIC'''
        p[0] = SKIP_STMT((p.lineno(1), p.lineno(1)))
        p.set_lineno(0, p.lineno(1))

    def p_stmt_error(self,p):
        '''stmt : error SEMIC'''
        print("Invalid statement near line {}".format(p.lineno(1)))

    def p_se(self, p):
        ''' se : stmt_expr
			   | empty'''
        p[0] = p[1]

    def p_e(self, p):
        ''' e : expr
			  | empty'''
        p[0] = p[1]

    def p_expr(self, p):
        # expr arith_op expr
        ''' expr : primary
				 | assign
				 | new_array
				 | expr PLUS expr
				 | expr MULT expr
				 | expr DIV expr
				 | expr MINUS expr
				 | expr AND expr
				 | expr OR expr
				 | expr EQUAL expr
				 | expr NEQUAL expr
				 | expr LESS expr
				 | expr GREATER expr
				 | expr GRTEQ expr
				 | expr LESEQ expr
				 | PLUS expr %prec UMINUS
				 | MINUS expr %prec UMINUS
				 | NOT expr'''

        if (len(p) == 2):
            p[0] = p[1]
            p.set_lineno(0, p.lineno(1))
        elif (len(p) == 4):
            p.set_lineno(0, p.lineno(3))
            p[0] = BINARY_EXP(p[2], p[1], p[3], (p.lineno(1), p.lineno(3)))

        else:
            p.set_lineno(0, p.lineno(2))
            if p[1] != "+":
                p[0] = UNARY_EXP(p[1], p[2], (p.lineno(1), p.lineno(2)))
            else:
                p[0] = p[2]

    def p_assign(self, p):
        ''' assign : lhs ASSN expr
				   | lhs PPLUS
				   | PPLUS lhs
				   | lhs MMINUS
				   | MMINUS lhs'''
        if (len(p) > 3):
            p[0] = ASSIGN_EXP(p[1], p[3], (p.lineno(1), p.lineno(3)))
            p.set_lineno(0, p.lineno(3))

        else:
            p.set_lineno(0, p.lineno(2))
            if (p[1] == "++"):
                p[0] = AUTO_EXP(p[2], "increment", "pre", (p.lineno(1), p.lineno(2)))
            elif (p[1] == "--"):
                p[0] = AUTO_EXP(p[2], "decrement", "pre", (p.lineno(1), p.lineno(2)))
            elif (p[2] == "++"):
                p[0] = AUTO_EXP(p[1], "increment", "post", (p.lineno(1), p.lineno(2)))
            else:
                p[0] = AUTO_EXP(p[1], "decrement", "post", (p.lineno(1), p.lineno(2)))

    def p_new_array(self, p):
        ''' new_array : NEW type nexpr base'''
        if (p[4] is not None):
            p[0] = NEW_ARR_EXP(p[3], p[4], (p.lineno(1), p.lineno(4)))
        else:
            p[0] = NEW_ARR_EXP(p[3], p[2], (p.lineno(1), p.lineno(3)))

    def p_nexpr(self, p):
        ''' nexpr : nexpr LEFTBr expr RIGHTBr
				  | LEFTBr expr RIGHTBr '''
        if (len(p) == 5):
            p[0] = p[1] + [p[3]]
            p.set_lineno(0, p.lineno(4))
        else:
            p[0] = [p[2]]
            p.set_lineno(0, p.lineno(3))

    def p_base(self, p):
        ''' base : lbr RIGHTBr base
				 | empty'''
        if (p[1] is not None):
            if (p[3] is not None):
                p[0] = "array(" + p[3] + ")"
                p.set_lineno(0, p.lineno(3))
            else:
                p[0] = "array(" + p[1] + ")"
                p.set_lineno(0, p.lineno(2))

    def p_lbr(self, p):
        '''lbr : LEFTBr'''
        p[0] = p[-2]

    def p_stmt_expr(self, p):
        ''' stmt_expr : assign
					  | method_invocation'''
        p[0] = p[1]

    def p_literal_NULL(self, p):
        ''' literal :  NULL'''
        p[0] = CONST_EXP("Null-constant",p[1], (p.lineno(1), p.lineno(1)),"null")
        p.set_lineno(0, p.lineno(1))

    def p_literal_int_constant(self,p):
        ''' literal : INT_CONSTANT '''
        p[0] = CONST_EXP("Integer_constant",p[1], (p.lineno(1), p.lineno(1)),"int")
        p.set_lineno(0, p.lineno(1))

    def p_literal_float_constant(self,p):
        ''' literal : FLOAT_CONSTANT'''
        p[0] = CONST_EXP("Float_constant",p[1], (p.lineno(1), p.lineno(1)),"float")
        p.set_lineno(0, p.lineno(1))
    def p_literal_string_constant(self,p):
        ''' literal : STRING_CONSTANT'''
        p[0] = CONST_EXP("String_constant",p[1], (p.lineno(1), p.lineno(1)),"string")
        p.set_lineno(0, p.lineno(1))

    def p_literal_boolean_constant(self,p):
        ''' literal : TRUE
                    | FALSE'''
        p[0] = CONST_EXP("Boolean_constant",p[1], (p.lineno(1), p.lineno(1)),"boolean")
        p.set_lineno(0, p.lineno(1))

    def p_primary_1(self, p):
        ''' primary : literal
					| this
					| super
					| lhs
					| method_invocation '''
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_primary_2(self, p):
        ''' primary	: LEFTPr expr RIGHTPr
					| NEW ID LEFTPr RIGHTPr
					| NEW ID LEFTPr arguments RIGHTPr'''
        if (len(p) == 4):
            p[0] = p[2]
            p.set_lineno(0, p.lineno(3))
        elif (len(p) == 5):
            p[0] = NEW_OBJ_EXP(p[2], None, (p.lineno(1), p.lineno(4)))
            p.set_lineno(0, p.lineno(4))
        else:
            p[0] = NEW_OBJ_EXP(p[2], p[4], (p.lineno(1), p.lineno(5)))
            p.set_lineno(0, p.lineno(5))

    def p_this(self, p):
        '''this : THIS'''
        p[0] = THIS_EXP((p.lineno(1), p.lineno(1)))
        p.set_lineno(0, p.lineno(1))

    def p_super(self, p):
        '''super : SUPER'''
        p[0] = SUPER_EXP((p.lineno(1), p.lineno(1)))
        p.set_lineno(0, p.lineno(1))

    def p_arguments(self, p):
        ''' arguments : expr inter_arguments'''

        if (p[2] is not None):
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

    def p_inter_arguments(self, p):
        ''' inter_arguments : COMMA expr inter_arguments
							| empty'''
        # (,expr)*
        if (p[1] is not None):
            if (p[3] is not None):
                p[0] = [p[2]] + p[3]
            else:
                p[0] = [p[2]]

    def p_lhs(self, p):
        ''' lhs : field_access
				| array_access'''
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_field_access(self, p):
        ''' field_access : primary PERIOD ID
						 | ID'''

        if (len(p) > 2):
            p[0] = FIELD_EXP(p[3], p[1], (p.lineno(1), p.lineno(3)))
            p.set_lineno(0, p.lineno(3))
        else:
            p.set_lineno(0, p.lineno(1))
            # Resovling the scope here
            # Identifying whether the variable is local or class reference expression
            # self.stack[len(self.stack)-1]

            for varlist in reversed(self.stack):
                for ivarlist in varlist:
                    if (p[1] == ivarlist.name):
                        p[0] = VAR_EXP(ivarlist,ivarlist.id, (p.lineno(1), p.lineno(1)))
                        return

            if self.CLASS_TABLE.children != []:

                if (p[1] in self.CLASS_NAME):
                    p[0] = CLASS_REF_EXP(p[1], (p.lineno(1), p.lineno(1)))
                    return

            # default condition
            p[0] = FIELD_EXP(p[1], THIS_EXP((p.lineno(1), p.lineno(1))), (p.lineno(1), p.lineno(1)))

    def p_array_access(self, p):
        ''' array_access : primary LEFTBr expr RIGHTBr'''
        p[0] = ARR_ACC_EXP(p[1], p[3], (p.lineno(1), p.lineno(4)))
        p.set_lineno(0, p.lineno(4))

    def p_method_invocation(self, p):
        ''' method_invocation : field_access LEFTPr RIGHTPr
							  | field_access LEFTPr arguments RIGHTPr'''
        #Place check here for varexpr

        if (len(p) == 4 and isinstance(p[1],FIELD_EXP)):
            p[0] = METHOD_CALL_EXP(p[1], None, (p.lineno(1), p.lineno(3)))
            p.set_lineno(0, p.lineno(3))
        elif(isinstance(p[1],FIELD_EXP)):
            p[0] = METHOD_CALL_EXP(p[1], p[3], (p.lineno(1), p.lineno(4)))
            p.set_lineno(0, p.lineno(4))
        else:
            print >> sys.stderr,"error : method invocation cannot be applied to %s at lineno %d" %(p[1].var.name,p.lineno(1))
            sys.exit()
    def p_empty(self, p):
        '''empty : '''
        pass

    # Error handling block
    def p_error(self,p):
        if p is None:
            print ("Unexpected end-of-file")
        else:
            print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
        self.parseSuccess = False
    precedence = (

        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
        ('right', 'ASSN'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('nonassoc', 'EQUAL', 'NEQUAL'),
        ('nonassoc', 'GREATER', 'LESS', 'LESEQ', 'GRTEQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('right', 'NOT'),
        ('right', 'UMINUS'),

    )
