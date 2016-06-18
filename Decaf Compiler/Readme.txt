HW6

The following directory contains the four modules , listed below:
1) decafc.py
2) decaflexer.py
3) decafparser.py
4) AST.py
5) TypeChecker.py
6) codegen.py
7) absmc.py

the new module added in this HW6

8) SSA.py

1) decafch.py:
   This file is the main top-level file. It contains the main python function that
   puts together the parser and lexer. It takes the filename as command line argument
   and does syntax checking.

2) decaflexer.py:
   This file contains the lexer for the decaf language.

3) decafparser.py:
   This file contains the PLY/yacc parser. This contains the grammar rule for the decaf.
   It check if the program is syntactically valid or not.

4) AST.py:
   This file contains the table and class definitions for the decaf's AST. Upon successful
   parsing the AST will be formed. The core of this AST is the class table which contains
   the information of all the classes in the input program.
   
5) TypeChecker.py:
   This file contains the definitions for evaluating the type constraints and for name resolution. 

6) codegen.py:
   This file has been changed and now translated the code to the MIPS assembly code.

7) absmc.py:
   This file contains the helper functions

8) SSA.py:
   This file contains the code to perform the liveness analysis and register allocation.

Assumption :
1) Every method defined in input file contains the return statement in the end.
   even if it has the void return type. (As stated by the instructor in the class)

   class A{
	public static void main(){
		...
		...
		return ;  //<-------This return statement is necessity
	}
   }
An overview of how the software function :

   Open the command line interpreter in the directory of decafch.py
   and execute the "python decafc.py filename"
   The filename contains the decaf code.

   After executing there will be two new file generated 
   1) filename.ami
   2) filename.asm

   In filename.ami we will be generating the intermediate code and then on this intermediate code after
   performing the register allocation the final output will be in filename.asm
   
   Example:
---------------------------------------------
   class A{
	public static void main(){
		int i;
		int n;
	
		n = 19;
		int sum;
		sum = 0;
		for(i = 0; i < n; i++){
			sum = sum + i;
		}
		return;
	}
   }   
-----------------------------------------------

the coressponding filename.ami will look like this :

-----------------------------------------------
.data 
sap: .space 0
.text
main_entry_point: 
	subu $sp, $sp, 32 	# Stack Frame setup 
	sw $ra, 28($sp) 	# Preserve the return address
	sw $fp, 24($sp) 	# Preserve the frame pointer
	addu $fp, $sp, 32 	# move frame pointer to the base of frame

	li $t0, 0 # this holds i
	li $t1, 0 # this holds n
	li $t2, 0 # this holds sum
	li $t3, 19
	move $t1, $t3 # Assign 1
	li $t4, 0
	move $t2, $t4 # Assign 1
	li $t5, 0
	move $t0, $t5 # Assign 1
L0:				#Beginning of for loop
		slt $t6, $t0, $t1
		beqz $t6, L2
		add $t7, $t2, $t0
		move $t2, $t7 # Assign 1
L1:				#update expression of for loop
		move $t8, $t0
		li $t9, 1
		add $t10, $t0, $t9
		move $t0, $t10 # Assign 1
		b L0
L2:				#End of for loop

	lw $ra, 28($sp) 	#restore the return address
	lw $fp, 24($sp) 	#restore the frame pointer
	addu $sp, $sp, 32 	#restore the stack pointer
	jr $ra				#Return
-----------------------------------------------------

Note : Our filename.ami will contains the comments. So please check this for any help on comments

the corresponding filename.asm will look like this :

-----------------------------------------------
.data 
sap: .space 0
.text
main_entry_point: 
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	li $t1, 0
	li $t2, 0
	li $t3, 0
	li $t0, 19
	move $t2, $t0
	li $t0, 0
	move $t3, $t0
	li $t0, 0
	move $t1, $t0
L0:
	slt $t0, $t1, $t2
	beqz $t0, L2
	add $t0, $t3, $t1
	move $t3, $t0
L1:
	
	li $t0, 1
	add $t0, $t1, $t0
	move $t1, $t0
	b L0
L2::
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra
----------------------------------------------
Note : this is the output after the register allocation has been done on the filename.ami


Overview of SSA.py : 


1) class IRNode(object):
   This class is used to represent the instruction in the intermediate code generation

2) class SSA_UTIL(object):
   This class contains the helper function and maps that helps to perform other funtion which will be described later in the text.

3) class BasicBlock(object):
   This class contains the definition of BasicBlock. As the name suggests it holds the information of the block.

4) class SSA_CONSTRUCTION(object):

	contens of the class
	--------------------------------------------------------------------------------------------------
        self.Use = {}           #Contains the Use set of the statement in the program
        self.Def = {}           #Contains the def set of the statement in the program
        self.In = {}            #Contains the In set of the statement in the program
        self.Out = {}           #Contains the Out set of the statement in the program
        self.InferenceGraph = {} #Contains the Inference Graph of the statement in the program
        self.spill = []         #Contains the registers which are spilled 
        self.Color = {}         #Contains the color assigned to each register in the Intermediate code



	Methods in the class :
        def ConstructBasicBlock1(self,SI,EI,InstructionSet,Target):
		This method construct the BasicBlock for the given procedure.
	
	def ConstructCFG(self):
		This method constructs the CFG after the Basic Blocks construction
	

	def ComputeUseDef(self):
		This method computes the Use-Def for the statements in the Basic Block

	def ComputeInOut(self):
		This method computes the In and Out set for the statements in the Basic Block

	def ComputeInferenceGraph(self):
		This method computes the inference Graph from the In and Out set

	def CreateEdge(self,vertices):
		This is the helper function for the  metho dComputeInferenceGraph(self).

	def GraphColoring(self):
		This method colors the graph and see if the graph can be colored without spilling but without generating the spill code.
		If the Coloring cannot be done without generating the spill code. Then it calls the "GraphColoringSpill(self)" method.

	def GraphColoringSpill(def):
		This method generates the spill code required.

	def getDifferentColor(self,C):
		This method is the helper function for the "GraphColoring" method.

	def Translate(self,SI,EI,InstructionSet):
		After performing register allocation this graphs translates the intermediate code to final code

	def getVertexSpill(self,Graph):
		Spill the vertex with largest degree

	def getAnode(self,Graph,reg):
        	Returns the node whose degree is less the reg

	def getUnionSuccessorset(self,index):
        	This method gives the union of the successor of block

	def getUse(self,statement):
        	Computes the Use set of the given statement

	def getDef(self,statement):
        	Give the set containing register defined in the statement


	The method described below are used to compute the SSA form:
	-----------------------------------------------------------------------
	def ComputeDominance(self):
        	This method Computes the Dominance of every node in the CFG

	def ComputeIDom(self):
        	This method Computes the immediate Dominator of the CFG node

	def ComputeDomTree(self):
        	This method Computes the Dominance Tree

    	def ComputePredecessor(self):
       		This method computes the set of predecessor of every node in the given CFG 

	def Phi_Nodes_Insertion(self):
        	The implementation of this method has not been provided. But this method will be used to insert Phi-Nodes

    	def Phi_Nodes_Rename(self):
        	The implementation of this method is not provided but this method will be used to rename Phi-Nodes

	Our SSA form is incomplete but still we have done 70% of the work for its computation. We have provided the implemenation of the necessary
	methods for its computation.

Additional features :
1)
	Our Program is able to compute the set of the nodes which needs to be spilled in case of spill occurs. With little more implementation we would have
	easily generated the functionality of spill code more robust but the deadline was approaching and we have to halt this work.

	In order to test the above features you can run this sample input program :
	--------------------------------------------------------------------------------
	class A{
	
		int g(int a, int b, int c, int d, int e){
			return a + b + c + d + e;
		}
		int f(int a, int b, int c, int d, int e){
			return a + b + c + d + e;
		}
		public static int main(){
			int a,b,c,d,e;
			int m,j;
			int r;
			m = g(a,b,c,d,e);
			j = f(a,b,c,d,e);
			r = m + j;
			return r;
		}
	}	 
	--------------------------------------------------------------------------------

	Upon the execution of the program. You will be given the set of register which needs to spilled.
	
2) 
	Our Program also workd for the floating point values partially.	




