import collections
import absmc

class IRNode(object):

    def __init__(self,irnode):
        self.irnode = irnode

class SSA_UTIL(object):

    def __init__(self):
        self.ProcedureIndex = []           #Contains the Index
        self.InstructMap1 = {'iadd' : 1,'isub' : 1,
                            'imul' : 1,'idiv' : 1,'imod' : 1,
                            'igt' : 1,'igeq' : 1,'ilt' : 1,'ileq' : 1,
                            'fadd' : 1,'fsub' : 1,'fmul' : 1,'fdiv' : 1,'fgt' : 1,
                            'fgeq' : 1,'flt' : 1,'fleq' : 1,'hload':1,
                            'move':2,'move_immed_i':5,'move_immed_j':5,
                            'ftoi':2,'itof':2,'halloc':2,'call':0,
                            'jmp':0,'ret':0, 'hstore':7, 'bz':6, 'bnz':6,
                            'save':0,'restore':3,
                            }
        self.ArgMap1 = { 'iadd' : 3,'isub' : 3,
                        'imul' : 3,'idiv' : 3,'imod' : 3,
                        'igt' : 3,'igeq' : 3,'ilt' : 3,'ileq' : 3,
                        'fadd' : 3,'fsub' : 3,'fmul' : 3,'fdiv' : 3,'fgt' : 3,
                        'fgeq' : 3,'flt' : 3,'fleq' : 3,'hload':3,
                        'move':2,'move_immed_i':2,'move_immed_j':2,
                        'ftoi':2,'itof':2,'halloc':2,'call':1,
                        'jmp':1,'ret':0, 'hstore':3, 'bz':2, 'bnz':2,
                        'save':1,'restore':1,
                        }

        self.InstructMap = {
                                'sub':1,'mul':1,'add':1,'div':1,
                                'sub.s':1,'mul.s':1,'add.s':1,'div.s':1,
                                'sne': 1, 'sne.s':1,'slt':1,'slt.s':1,
                                'sgt':1,'sgt.s':1,'sge':1,'sge.s':1,
                                'sle':1,'sle.s':1,'jal':0,'syscall':0,
                                'subu':2,'sw':8,'sw.s':8,'lw':9,'lw.s':9,'jr':0,'b':0,
                                'beqz':6,'move':2,'move.s':2,'li.s':5,'li':5,
                                'mtc1':10,'cvt.s.w':2,'la':5,'addu':1,
                            }

        self.ArgMap = {     'addu':3,
                            'sub':3,'mul':3,'add':3,'div':3,
                            'sub.s':3,'mul.s':3,'add.s':3,'div.s':3,
                            'sne': 3, 'sne.s':3,'slt':3,'slt.s':3,
                            'sgt':3,'sgt.s':3,'sge':3,'sge.s':3,
                            'sle':3,'sle.s':3,'jal':0,'syscall':0,
                            'subu':3,'sw':2,'sw.s':2,'lw':2,'lw.s':2,'jr':1,'b':1,
                            'beqz':2,'move':2,'move.s':2,'li.s':2,'li':2,
                            'mtc1':2,'cvt.s.w':2,'la':2,
                        }
class BasicBlock(object):

    def __init__(self,id):
        self.id = id
        self.InstructionList = {}

    def Insert_Instruction(self,key,instruction):
        self.InstructionList[key] = instruction

class SSA_CONSTRUCTION(object):

    def __init__(self,ssa_util,fileName):

        self.SSA_UTIL = ssa_util
        self.Leader = []
        self.BlockList = []
        self.LabelToBlockMap = {}
        self.BlockCounter = 0
        self.predecessor = {}
        self.CFG = {}           #Contains the CFG of the procedure
        self.DomiTree = {}      #Contains the Dominator Tree
        self.Dom = {}
        self.IDom = {}
        self.Use = {}           #Contains the Use set of the statement in the program
        self.Def = {}           #Contains the def set of the statement in the program
        self.In = {}            #Contains the In set of the statement in the program
        self.Out = {}           #Contains the Out set of the statement in the program
        self.InferenceGraph = {} #Contains the Inference Graph of the statement in the program
        self.spill = []         #Contains the registers which are spilled
        self.Color = {}         #Contains the color assigned to each register in the Intermediate code
        self.f = fileName

    def Wipe(self):

        self.Leader = []
        self.BlockList = []
        self.LabelToBlockMap = {}
        self.BlockCounter = 0
        self.predecessor = {}
        self.CFG = {}
        self.DomiTree = {}
        self.Dom = {}
        self.IDom = {}
        self.Use = {}
        self.Def = {}
        self.In = {}
        self.Out = {}
        self.InferenceGraph = {}
        self.spill = []
        self.Color = {}

    def Perform_Optimization(self,SI,EI,InstructionSet):
        counter = SI
        # print "------start new block------"
        Target = {}
        while counter < EI:
            if(self.IsLabel(InstructionSet[counter].irnode)):
                Target[InstructionSet[counter].irnode[0]] = counter

            counter = counter + 1

        self.ConstructBasicBlock1(SI,EI,InstructionSet,Target)
        self.Translate(SI,EI,InstructionSet)

    def ConstructBasicBlock1(self,SI,EI,InstructionSet,Target):
        # This method construct the BasicBlock for the given procedure.

        self.BlockCounter = 0
        self.Wipe()
        length = len(InstructionSet)
        counter = SI + 1
        while(counter < EI):
            block = BasicBlock(self.BlockCounter)
            self.BlockCounter = self.BlockCounter + 1
            if(self.IsLabel(InstructionSet[counter].irnode)):
                self.LabelToBlockMap[InstructionSet[counter].irnode[0]] = block.id

            block.Insert_Instruction(counter,InstructionSet[counter].irnode)
            self.BlockList = self.BlockList + [block]
            counter = counter + 1

        for block in self.BlockList:
            # print "--------------",block.id,"--------------"
            block.InstructionList = collections.OrderedDict(sorted(block.InstructionList.items()
                                                       , key = lambda t:t[0]))
            # for key in block.InstructionList:
            #     print key , block.InstructionList[key]
            # print "---------block end----------------------"

        # print "Label to Block"
        # print self.LabelToBlockMap
        self.ConstructCFG()

    def ConstructBasicBlock(self,SI,EI,InstructionSet,Target):
        #		This method construct the BasicBlock for the given procedure.

        self.Wipe()
        length = len(InstructionSet)
        # print "---",length,"---"
        self.BlockCounter = 0
        self.Leader = self.Leader +[SI + 1]
        counter = SI + 1
        # print "branching instruction"
        while(counter < EI):
            if(self.IsBranchInstruction(InstructionSet[counter].irnode)):
                self.Leader = self.Leader + [counter + 1] + [self.getTargetIndex(InstructionSet[counter].irnode,
                                                                            Target)]
            counter = counter + 1

        WorkList = set(self.Leader)
        # print WorkList
        while WorkList:
            x = self.getSmallestIndex(WorkList)
            # print "min at this",x
            WorkList = WorkList - set([x])
            # print WorkList
            block = BasicBlock(self.BlockCounter)
            self.BlockCounter = self.BlockCounter + 1

            #block.Insert_Instruction(x,InstructionSet[x].irnode)
            block.InstructionList[x] = InstructionSet[x].irnode
            if(self.IsLabel(InstructionSet[x].irnode)):
                self.LabelToBlockMap[InstructionSet[x].irnode[0]] = block.id

            iter = x + 1
            while((iter < EI) and (iter not in self.Leader )):
                #block.Insert_Instruction(iter,InstructionSet[iter].irnode)
                if(self.IsLabel(InstructionSet[iter].irnode)):
                    self.LabelToBlockMap[InstructionSet[iter].irnode[0]] = block.id
                block.InstructionList[iter] = InstructionSet[iter].irnode

                iter = iter + 1
            self.BlockList = self.BlockList + [block]


        #print the blocks

        for block in self.BlockList:
            # print "--------------",block.id,"--------------"
            block.InstructionList = collections.OrderedDict(sorted(block.InstructionList.items()
                                                       , key = lambda t:t[0]))
            # for key in block.InstructionList:
            #     print key , block.InstructionList[key]
            # print "---------block end----------------------"
        # print "Label to Block"
        # print self.LabelToBlockMap
        self.ConstructCFG()

    def ConstructCFG(self):

        # print "total number of blocks",self.BlockCounter
        for block in self.BlockList:
            self.CFG[block.id] = []
            irnode =  block.InstructionList.items()[-1] #last instruction
            #print irnode[1][0],"last instruction"
            if(self.IsBranchInstruction(irnode[1])):
                if(irnode[1][0] == 'bz' or irnode[1][0] == 'bnz'):
                    self.CFG[block.id] =  [self.LabelToBlockMap[irnode[1][2]]] + [block.id+1] + self.CFG[block.id]
                else: #if it is jmp then
                    self.CFG[block.id] = [self.LabelToBlockMap[irnode[1][1]]] + self.CFG[block.id]
            else:
                if(irnode[1][0] == 'jr'):
                    self.CFG[block.id] = [-1] + self.CFG[block.id]
                else:
                    self.CFG[block.id] = [block.id+1] + self.CFG[block.id]

        # print "CFG : ",self.CFG
        self.ComputeUseDef()
        # self.CFG = {}
        # self.CFG[0] = [1]
        # self.CFG[1] = [2,5]
        # self.CFG[2] = [3]
        # self.CFG[3] = [1,4]
        # self.CFG[4] = [-1]
        # self.CFG[5] = [6,8]
        # self.CFG[6] = [7]
        # self.CFG[7] = [3]
        # self.CFG[8] = [7]
        # print "New CFG: ",self.CFG
        # self.ComputePredecessor()
        # print "predecssor : ",self.predecessor
        # self.ComputeDominance()

    def ComputeUseDef(self):
        for block in self.BlockList:
            self.Use[block.id] = set([])
            self.Def[block.id] = set([])

            for statement in block.InstructionList:

                use = self.getUse(block.InstructionList[statement])
                def_ = self.getDef(block.InstructionList[statement])
                self.Use[block.id] = self.Use[block.id].union(use)
                self.Def[block.id] = self.Def[block.id].union(def_)

        # print "this is use"
        # for key in self.Use:
        #     print key , self.Use[key]

        # print "this is def"
        # for key in self.Def:
        #     print key , self.Def[key]

        self.ComputeInOut()
        # print "This is InSet"
        # for key in self.In:
        #     print key , self.In[key]

        # print "This is OutSet"
        # for key in self.Out:
        #     print key , self.Out[key]

        # print "This is in-out"
        # for key in self.Out:
        #     print key , self.In[key] - self.Out[key]

        self.ComputeInferenceGraph()

    def ComputeInOut(self):

        for i in range(self.BlockCounter - 1, -1, -1):
            self.In[i] = set([])    #starting with least fixed point
            self.Out[i] = set([])   #Starting with least fixed point

        changed = True
        while(changed):
            changed = False

            for i in range(self.BlockCounter - 1, -1, -1):
                temp = self.getUnionSuccessorset(i)
                temp1 = temp - self.Def[i]
                temp2 = self.Use[i].union(temp1)

                if(temp != self.Out[i] or temp2 != self.In[i]):

                    self.Out[i] = temp
                    self.In[i] = temp2
                    changed = True

    def ComputeInferenceGraph(self):

        for key in self.In:
            #if(len(self.In[key]) > 1):
            self.CreateEdge(list(self.In[key]))

        for key in self.InferenceGraph:
            self.InferenceGraph[key] = self.InferenceGraph[key] - set([key])

        # print "The edges of inference graph"
        #
        # for key in self.InferenceGraph:
        #     print key , self.InferenceGraph[key]

        self.GraphColoring()

    def CreateEdge(self,vertices):
        for elements in vertices:
            if elements not in self.InferenceGraph:
                self.InferenceGraph[elements] = set([])

        for i in range(0,len(vertices)):
            self.InferenceGraph[vertices[i]]=self.InferenceGraph[vertices[i]].union(set(vertices[i+1:]))

        rev = vertices[::-1]

        for i in range(0,len(rev)):
            self.InferenceGraph[rev[i]] = self.InferenceGraph[rev[i]].union(set(rev[i+1:]))

    def GraphColoring(self):

        Graph =  dict(self.InferenceGraph)
        stack = absmc.Stack([])

        self.Color = {}
        while Graph:

            vertex = self.getAnode(Graph,8)
            if(vertex == -1):
                vertex = self.getVertexSpill(Graph)
                print vertex
            E = Graph[vertex]   #Set of edges on vertex v
                                #Removing Edges
            del Graph[vertex]   #Remove the entry

            for elements in list(E):
                Graph[elements] = Graph[elements] - set([vertex])
            stack.Push((vertex,E))
        spill  = False
        while not stack.isEmpty():
            tup_vE = stack.Pop()

            Graph[tup_vE[0]] = tup_vE[1]

            for elements in list(Graph[tup_vE[0]]):
                Graph[elements] = Graph[elements].union(set([tup_vE[0]]))

            C = set([])

            for elements in list(Graph[tup_vE[0]]):
                if(elements in self.Color):
                    C = C.union(set([self.Color[elements]]))
            # print "This is the ", tup_vE[0]
            # print "This is the edges",list(Graph[tup_vE[0]])
            # print "This is the color set ",C
            if(len(C) < 8):
                self.Color[tup_vE[0]] = self.getDifferentColor(C)
            else:
                print "Spill needed "
                # exit()
                spill = True
                break

        if(spill):
            self.GraphColoringSpill()

            # print "color assigned to the %s is %d"%(tup_vE[0],self.Color[tup_vE[0]])
        # for key in self.Color:
        #     print key , self.Color[key]

    def GraphColoringSpill(self):

        Graph =  dict(self.InferenceGraph)
        stack = absmc.Stack([])

        self.Color = {}
        while Graph:

            vertex = self.getAnode(Graph,7)
            if(vertex == -1):
                spill_vertex = self.getVertexSpill(Graph)
                self.Spill(spill_vertex)
                E = Graph[spill_vertex]   #Set of edges on vertex v
                                #Removing Edges
                del Graph[spill_vertex]   #Remove the entry

                for elements in list(E):
                    Graph[elements] = Graph[elements] - set([spill_vertex])
                vertex = self.getAnode(Graph,7)
                if(vertex == -1):
                    continue

            E = Graph[vertex]   #Set of edges on vertex v
                                #Removing Edges
            del Graph[vertex]   #Remove the entry

            for elements in list(E):
                Graph[elements] = Graph[elements] - set([vertex])

            if(vertex != -1):
              stack.Push((vertex,E))

        while not stack.isEmpty():
            tup_vE = stack.Pop()

            Graph[tup_vE[0]] = tup_vE[1]

            for elements in list(Graph[tup_vE[0]]):
                Graph[elements] = Graph[elements].union(set([tup_vE[0]]))

            C = set([])

            for elements in list(Graph[tup_vE[0]]):
                if(elements in self.Color):
                    C = C.union(set([self.Color[elements]]))
            # print "This is the ", tup_vE[0]
            # print "This is the edges",list(Graph[tup_vE[0]])
            # print "This is the color set ",C
            #if(len(C) < 8):
            self.Color[tup_vE[0]] = self.getDifferentColor(C)

        #     print "color assigned to the %s is %d"%(tup_vE[0],self.Color[tup_vE[0]])
        # for key in self.Color:
        #     print key , self.Color[key]

    def Spill(self,vertex):
            self.spill = self.spill + [vertex]
            print "spil list : ",self.spill

    def getDifferentColor(self,C):
            if(len(C) == 0):
                return 0

            counter = 0
            while counter < 8:
                if(counter not in C):
                    return counter
                counter +=1

    def getVertexSpill(self,Graph):

        #Spill the vertex with largest degree
        max = 0
        vertex = -1
        for key in Graph:
            if max  < len(Graph[key]):
                max = len(Graph[key])
                vertex = key

        print "This vertex is spilled : ",vertex
        return vertex

    def getAnode(self,Graph,reg):
        #Returns the node whose degree is less the reg
        for key in Graph:
            if len(Graph[key]) < reg:
                return key
        return -1


    def getUnionSuccessorset(self,index):
        #This method gives the union of the successor of block
        if(self.CFG[index] == [-1]):
            return set([])

        final = set([])
        for element in self.CFG[index]:
            final  = final.union(self.In[element])

        return final

    def getUse(self,statement):
        #Computes the Use set of the given statement
        instr = self.SSA_UTIL.InstructMap.get(statement[0],4)
        ret_set = set([])

        if(instr == 0):
            ret_set = set([])
        elif(instr  == 1):

           if(statement[2][0:2] == '$t'):
               ret_set = ret_set.union(set([statement[2]]))
           if(statement[3][0:2] == '$t'):
               ret_set = ret_set.union(set([statement[3]]))

        elif(instr == 2): #move,ftoi,itof,halloc
            if(statement[2][0:2] == '$t'):
                ret_set = set([statement[2]])


        elif(instr == 6): #bz,bnz
            if(statement[1][0:2] == '$t'):
                ret_set = set([statement[1]])

        elif(instr == 8):
            if(statement[1][0:2] == '$t'):
                ret_set = ret_set.union(set([statement[1]]))
            k = statement[2][-4:]
            k = k[:3]

            if(k[0:2] == '$t'):
                ret_set = ret_set.union(set([k]))
            else:
                k = statement[2][-5:]
                k = k[0:4]
                if(k[0:2] == '$t'):
                    ret_set = ret_set.union(set([k]))
        elif(instr == 9):
            k = statement[2][-4:]
            k = k[:3]
            if(k[0:2] == '$t'):
                ret_set = ret_set.union(set([k]))
            else:
                k = statement[2][-5:]
                k = k[0:4]
                if(k[0:2] == '$t'):
                    ret_set = ret_set.union(set([k]))

        elif(instr == 10):
            if(statement[1][0:2] == '$t'):
                ret_set = ret_set.union(set([statement[1]]))

        else:
            ret_set =  set([])

        return ret_set

    def getDef(self,statement):
        #Give the set containing register defined in the statement
        instr = self.SSA_UTIL.InstructMap.get(statement[0],4)

        if(instr  != 0 and instr != 4 and instr != 6 and instr!= 8 and statement[1][0:2] == '$t'):
            return set([statement[1]])
        elif(instr == 10 and statement[2][0:2] == '$t'):
            return set([statement[2]])
        else:
            return set([])

    def ComputeDominance(self):
        #This method Computes the Dominance of every node in the CFG
        AN = set([])
        for i in range(0,9): #self.BlockCounter
            AN = AN.union(set([i]))
        self.Dom[0] = set([0])
        for i in range(1,9):#self.BlockCounter
            self.Dom[i] = AN
        changed = True
        while(changed):
            changed = False

            for i in range(1,9): #self.BlockCounter
                inter_pred = self.getInterPredecssor(i,AN)
                temp = set([i]).union(inter_pred)

                if(temp != self.Dom[i]):
                    self.Dom[i] = temp
                    changed = True
        print self.Dom
        self.ComputeIDom()


    def Translate(self,SI,EI,InstructionSet):

        action = self.SSA_UTIL.ArgMap.get(InstructionSet[SI].irnode[0],0)
        str1 = self.getString(InstructionSet[SI].irnode,action)
        self.f.write(str1)
        counter = SI + 1
        self.f.write("\n")

        while(counter < EI):
            if(InstructionSet[counter].irnode[0][0:1] != 'L'): #do not give tab in case of Labels
                self.f.write("\t")
            action = self.SSA_UTIL.ArgMap.get(InstructionSet[counter].irnode[0],0)

            str1 = self.getString(InstructionSet[counter].irnode,action)
            self.f.write(str1)
            self.f.write("\n")
            counter = counter + 1

    def getString(self,irnode,action):
        #This method converts the code and maps the register to new
        #register after performing the register allocation
        if(action == 0):
            if(irnode[0][0:1] == 'L'):
                str1 = irnode[0]+":"
            else:
                str1 = irnode[0]
        elif(action == 1):

            if(irnode[1] in self.Color ):
                str1 = irnode[0]+" "+"$t"+str(self.Color[irnode[1]])
            elif(irnode[1][0:2] != '$t'):
                str1 = irnode[0]+" "+irnode[1]
            else:
                str1 = ""

        elif(action == 2):

            if(irnode[1][0:2] != '$t'):
                arg1 = irnode[1]
            else:
                #This means it is the temporary register
                if(irnode[1] in self.Color):
                    arg1 = "$t"+str(self.Color[irnode[1]])
                else:#Uncessary code No one uses this register, this is just defined
                    return ""

            if(irnode[0][0:2] == 'li' or irnode[2][0:2] != '$t'):
                if(irnode[2][0] == '('):
                    k = irnode[2][-4:]
                    k = k[:3]

                    if(k[0:2] == '$t'):
                        if( k in self.Color):
                            arg2 = "($t"+str(self.Color[k])+")"
                        else:
                            return ""
                    else:
                        k = irnode[2][-5:]
                        k = k[0:4]
                        if(k[0:2] == '$t'):
                            if(k in self.Color):
                                arg2 = "($t"+str(self.Color[k])+")"
                            else:
                                return ""
                        else:
                            arg2 = str(irnode[2])

                else:
                    arg2 = str(irnode[2])
            else:
                if(irnode[2] in self.Color):
                    arg2 = "$t"+str(self.Color[irnode[2]])
                else:
                    arg2 = irnode[2]
            str1 = irnode[0]+" "+arg1+", "+arg2

        else: #(action == 3):
            if(irnode[1][0:2] != '$t'):
                arg1 = irnode[1]
            else:
                #This means this is the temporary register
                if(irnode[1] in self.Color):
                    arg1 = "$t"+str(self.Color[irnode[1]])
                else:#Uncessary code No one uses this register, this is just defined
                    return ""
            if(irnode[2][0:2] != '$t'):
                arg2 = irnode[2]
            else:
                if(irnode[2] in self.Color):
                    arg2 = "$t"+str(self.Color[irnode[2]])
                else:
                    arg2 = irnode[2]

            if(irnode[3][0:2] != '$t'):
                arg3 = irnode[3]
            else:
                if(irnode[3] in self.Color):
                    arg3 = "$t"+str(self.Color[irnode[3]])
                else:
                    arg3 = irnode[3]

            str1 = irnode[0]+" "+arg1+", "+arg2+", "+arg3

        return str1
    def Phi_Nodes_Insertion(self):
        pass

    def Phi_Nodes_Rename(self):
        pass

    def IsBranchInstruction(self,irnode):

        if irnode[0] == 'bz' or irnode[0] == 'bnz' or irnode[0] == 'jmp':
            return True
        return False

    def IsLabel(self,irnode):
        if(irnode[0][0:1] == "L"):
            return True
        return False

    def getTargetIndex(self,irnode,Target):

        if irnode[0] == 'bz':
            return Target[irnode[2]]
        elif irnode[0] == 'bnz':
            return Target[irnode[2]]
        else:
            return Target[irnode[1]]

    def IsListEmpty(self,List):

        if(List == []):
            return True
        return False

    def getSmallestIndex(self,List):

        min = 10000000
        for element in List:
            if element < min :
                min = element

        return min

    def ComputePredecessor(self):
        #This method computes the set of predecessor of every node in the given CFG
        self.predecessor[0] = -2
        for i in range(1,9): #self.BlockCounter
            self.predecessor[i] = []
            for j in range(0,9): #self.BlockCounter
                if i in self.CFG[j]:
                    self.predecessor[i] = self.predecessor[i] + [j]

    def getInterPredecssor(self,i,AN):
        #Computes the intersection of the predecessor
        final_set = AN
        for j in self.predecessor[i]:
            final_set = final_set.intersection(self.Dom[j])
        return final_set

    def ComputeIDom(self):
        #Computes the immediate Dominator of the CFG node
        self.IDom[0] = -2
        print self.Dom
        for element in range(1,9):#self.BlockCounter
            max = -1
            for dom in self.Dom[element]:
                if(dom!=element and max < dom):
                    max = dom
                    self.IDom[element] = dom

        print "This is IDOM : ",self.IDom
        self.ComputeDomTree()

    def ComputeDomTree(self):
        #Computes the Dominance Tree
        for key in self.IDom:
            if(self.IDom[key] != -2):
                self.DomiTree[self.IDom[key]] = []

        for key in self.IDom:
            if(self.IDom[key] != -2):
                self.DomiTree[self.IDom[key]] = self.DomiTree[self.IDom[key]] + [key]

        print "This is DominatorTree : ",self.DomiTree
