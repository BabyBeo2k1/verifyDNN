import numpy as np
class DeepPoly:
    def __init__(self,nvar):
        self.nvar=nvar
        self.upper_relation=np.zeros((nvar+1,nvar))
        self.lower_relation=np.zeros((nvar+1,nvar))
        self.weight=np.zeros((nvar+1,nvar))
        self.reluout=[]
        self.relu=[]
        self.inputs=[self.nvar]
        self.bounds=np.ones((nvar,2))*np.array([[-np.inf,np.inf]])
        self.property=np.zeros((nvar+1,)) #sum of this want to prove <=0
    def addWeight(self,in_var,  weight, out_var):
        
        self.weight[in_var][out_var]=weight
    def addReLU(self, in_var,out_var):
        self.reluout.append(out_var)
        self.relu.append((in_var,out_var))
    def addBoundInput(self, in_var, lb=-np.inf,ub=np.inf):
        self.inputs.append(in_var)
        self.upper_relation[self.nvar][in_var]=ub
        self.lower_relation[self.nvar][in_var]=lb
        self.bounds[in_var]=[lb,ub]
    def addOutputProperty(self,var,weight):
        self.property[var]=weight
    def addOutputRHS(self,weight):
        self.property[self.nvar]=-weight
    def setBounds(self,var):
        if var in self.inputs or (self.bounds[var]!=[-np.inf,np.inf]).any():
            return
        for relu in self.relu:
            if relu[1]==var:
                self.setBounds(relu[0])
                uj=self.bounds[relu[0]][1]
                lj=self.bounds[relu[0]][0]
                self.bounds[var][1]=max(0,uj)
                self.bounds[var][0]=max(0,lj)
                if self.bounds[relu[0]][0]>=0:
                    self.upper_relation[:,var]=self.upper_relation[:,relu[0]]
                    self.lower_relation[:,var]=self.upper_relation[:,relu[0]]
                elif self.bounds[relu[0]][1]>=0:
                    self.upper_relation[:,var]=float(uj/(uj-lj))*self.upper_relation[:,relu[0]]
                    self.upper_relation[self.nvar][var]=-float(uj*lj/(uj-lj))
                    self.lower_relation[:,var]=self.alpha*self.upper_relation[:,relu[0]]
                return
        self.bounds[var]=[0,0]
        self.upper_relation[:,var]=self.weight[:,var]
        self.lower_relation[:,var]=self.weight[:,var]
        while self.check_up_sub(var):
            for i in range(self.nvar):
                if i in self.reluout:
                    x=self.upper_relation[:,var]
                    if self.upper_relation[i][var]>0:
                        self.setBounds(i)
                        self.upper_relation[:,var]+=self.upper_relation[i][var]*self.upper_relation[:,i]
                        self.upper_relation[i][var]=0
                    elif self.upper_relation[i][var]<0:
                        self.setBounds(i)
                        self.upper_relation[:,var]+=self.upper_relation[i][var]*self.lower_relation[:,i]
                        self.upper_relation[i][var]=0
                elif i in self.inputs:
                    continue
                else:
                    if self.weight[i][var]!=0:
                        self.setBounds(i)
                        self.upper_relation[:,var]+=self.weight[i][var]*self.weight[:,i]
                        self.upper_relation[i][var]=0
        while self.check_low_sub(var):
            for i in range(self.nvar):
                if i in self.reluout:
                    if self.lower_relation[i][var]>0:
                        self.setBounds(i)
                        self.lower_relation[:,var]+=self.lower_relation[i][var]*self.lower_relation[:,i]
                        self.lower_relation[i][var]=0
                    elif self.lower_relation[i][var]<0:
                        self.setBounds(i)
                        self.lower_relation[:,var]+=self.lower_relation[i][var]*self.upper_relation[:,i]
                        self.lower_relation[i][var]=0
                elif i in self.inputs:
                    continue
                else:
                    if self.weight[i][var]!=0:
                        self.setBounds(i)
                        self.lower_relation[:,var]+=self.weight[i][var]*self.weight[:,i]
                        self.lower_relation[i][var]=0
        for j in self.inputs:
            if j == self.nvar:
                self.bounds[var][0]+=self.lower_relation[self.nvar][var]
                self.bounds[var][1]+=self.upper_relation[self.nvar][var]
                continue
            uj=self.bounds[j][1]
            lj=self.bounds[j][0]
            if self.upper_relation[j][var]>0:
                self.bounds[var][1]+=self.upper_relation[j][var]*uj
            else:
                self.bounds[var][1]+=self.upper_relation[j][var]*lj

            if self.lower_relation[j][var]>0:
                self.bounds[var][0]+=self.lower_relation[j][var]*lj
            else:
                self.bounds[var][0]+=self.lower_relation[j][var]*uj
    def check_up_sub(self,var):
        for idx,w in enumerate(self.upper_relation[:,var]):
            if idx in self.inputs:
                continue
            else:
                if w!=0:
                    return True
        return False
    def check_low_sub(self,var):
        for idx,w in enumerate(self.lower_relation[:,var]):
            if idx in self.inputs:
                continue
            else:
                if w!=0:
                    return True
        return False
    
    def check_safe(self):
        safe=0
        for j in range(self.nvar):
            if self.property[j]>0:
                safe+=self.property[j]*self.bounds[j][1]
            else:
                safe+=self.property[j]*self.bounds[j][0]
        safe+=self.property[self.nvar]
        if safe<=0:
            return True,safe
        else:
            return False,safe     
    def check_converge(self):
        for i in range(self.nvar):
            if not i in self.inputs:
                if self.property[i]!=0:
                    return True
        return False
    def solve(self,alpha):
        if not(0<=alpha<=1):
            raise ValueError("alpha in range 0 to 1 only")
        self.alpha=alpha
        for var in range(self.nvar):
            print("check "+str(var))
            if var in self.inputs:
                continue 
            self.setBounds(var)
            print(self.upper_relation[:,var])
            print(self.lower_relation[:,var])
        print(self.upper_relation)
        print(self.bounds)
        
        while self.check_converge():
            for i in range(self.nvar):
                if self.property[i]>0:
                    print(self.property)
                    self.property+=self.upper_relation[:,i]*self.property[i]
                    
                    self.property[i]=0
                elif self.property[i]<0:
                    print(self.property)
                    self.property+=self.lower_relation[:,i]*self.property[i]
                    self.property[i]=0

            print(self.property)
            print(self.check_safe()[1])
        if self.check_safe()[0]:
            print("SAT")
        else:
            print("not really unsat but you should change algorithm :>")
            print(self.check_safe()[1])