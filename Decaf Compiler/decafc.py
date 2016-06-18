from decaflexer import DECAFLEX
from decafparser import DECAFPARSER
from TypeChecker import *
from codegen import *
import sys

def main(fileName):
    fileRef = open(fileName, 'r')
    inputcode = ""                                      #String to store code
    #Block to put code lines in the inputcode string
    for line in fileRef:
        inputcode = inputcode + line
    
    decafLex = DECAFLEX()                               # lexer object
    decafLex.build()
    decafParser = DECAFPARSER(decafLex.tokens)          # parser object
    decafParser.parser.parse(inputcode,decafLex)

    if decafParser.parseSuccess:                        # Check whether the input program is syntactically valid
        #decafParser.CLASS_TABLE.PRINT()                 # If Parse is succes then print

        check = TypeChecker(decafParser.CLASS_TABLE)
        if(check.error == False):
            CodeGen(check.subtypetuple,decafParser.CLASS_TABLE,fileName)

if __name__ == '__main__':
    main(sys.argv[1]) 