import re
import sys
import ply.lex as lex

class DECAFLEX(object):
    RESWORD = ('BOOLEAN', 'BREAK', 'CONTINUE', 'CLASS', 'DO',
                'ELSE', 'EXTENDS', 'FALSE', 'FLOAT', 'FOR', 'IF',
                'INT', 'NEW', 'NULL', 'PRIVATE', 'PUBLIC','RETURN','STATIC',
                'SUPER', 'THIS', 'TRUE', 'VOID', 'WHILE',)
    
    #ReserveWords
    RESWORDDICT = {
        'boolean' : 'BOOLEAN',
        'break' : 'BREAK', 
        'continue':'CONTINUE', 
        'class' : 'CLASS', 
        'do' : 'DO', 
        'else' : 'ELSE',
        'extends' : 'EXTENDS', 
        'false' : 'FALSE', 
        'float' : 'FLOAT', 
        'for' : 'FOR',
        'if' : 'IF', 
        'int' : 'INT', 
        'new' : 'NEW',
        'null' : 'NULL', 
        'private' : 'PRIVATE',
        'public' : 'PUBLIC', 
        'return' : 'RETURN', 
        'static' : 'STATIC', 
        'super' : 'SUPER',
        'this' : 'THIS', 
        'true' : 'TRUE', 
        'void' : 'VOID', 
        'while' : 'WHILE',
    }
    
    #List of Tokens
    tokens = RESWORD + (    
                'ID',             
                'PLUS', 'MINUS', 'MULT', 'DIV',
                'NOT', 'AND', 'OR', 'EQUAL', 'NEQUAL',
                'RIGHTBr', 'LEFTBr', 'RIGHTPr', 'LEFTPr',
                'COMMA', 'PERIOD', 'SEMIC', 'COLON', 'MMINUS',
                'PPLUS', 'ASSN', 'GRTEQ', 'LESEQ', 'LESS', 'GREATER',
                'INT_CONSTANT','FLOAT_CONSTANT', 'STRING_CONSTANT',
                'LBRACE','RBRACE',
                )
            
  
    # List of Rules  
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULT = r'\*'
    t_DIV = r'/'
    t_NOT = r'!'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_EQUAL = r'=='
    t_NEQUAL = r'!='
    t_GREATER = r'>'
    t_LESS = r'<'
    t_LESEQ = r'<='
    t_GRTEQ = r'>='
    t_ASSN = r'='
    t_PPLUS = r'\+\+'
    t_MMINUS = r'--'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_SEMIC = r';'
    t_COLON = r':'
    t_LEFTPr = r'\('
    t_RIGHTPr = r'\)'
    t_LEFTBr = r'\['
    t_RIGHTBr = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    
    # Define a rule so we can track line numbers
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    
    def t_COMMENT(self,t):
        r'//.*|/\*(.|\n)*?\*/'
        pass
    # No return value. Token discarded
    
    def t_ID(self,t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        t.type = self.RESWORDDICT.get(t.value,"ID");
        return t
    
    def t_STRING_CONSTANT(self,t):
        r'"([^"\\\n\t]*?(\\\\|\\n|\\t|\\")*?[^"\\\n\t]*?)*"'
        return t
        
    def t_FLOAT_CONSTANT(self,t):
        r'-?[0-9]+(\.[0-9]+)?[e|E][+|-]?[0-9]+|-?[0-9]+\.[0-9]+'
        t.value = float(t.value)
        return t

    
    def t_INT_CONSTANT(self,t):
        r'\d+'
        t.value = int(t.value)
        return t

        
    
    #Spaces and tabs are to ignored    
    t_ignore = " \t"
    
    #Error handling block
    def t_error(self,t):
        # Skip tokens until next semi colon
        
        #block to find position of error in a line
        def getPosition():
            last_cr = t.lexer.lexdata.rfind('\n',0,t.lexpos)
            if last_cr < 0:
                last_cr = 0
            return (t.lexpos - last_cr) + t.lexer.lexdata.count('\t',last_cr,t.lexpos)*3
        if t.value.find(";")==-1:
            print >> sys.stderr,"Illegal token at line %s position %s near '%s'" %(t.lineno ,getPosition(), t.value)
            t.lexer.skip(len(t.value))   
        else:
            print >> sys.stderr,"Illegal token at line %s position %s near '%s'" %(t.lineno ,getPosition(), t.value[0:t.value.find(";")])
            t.lexer.skip(t.value.find(";"))    


    #Build the lexer 
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
    
    #Method to take input to be tokenized
    def input(self, inputcode):
        self.lexer.input(inputcode)
    
    #Method to return token
    def token(self):
        return self.lexer.token()