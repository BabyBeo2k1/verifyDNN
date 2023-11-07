import numpy as np
class Reluplex:
    def __init__(self,nvar) -> None:
        self.nvar=nvar
        self.weight=np.zeros((nvar+1,nvar+1))
        self.relu_in=[]
        self.relu_out=[]
        self.relu_timeout=[]
        self.inputs=[0]
        self.bounds=np.ones((nvar+1,2))*np.array([[-np.inf,np.inf]])
        self.property=np.zeros((nvar+1,)) #sum of this want to prove <=0
        self.activation=[]
        self.asign=np.zeros((nvar,))
    def setTableau(self):
        tableau=[[i for i in range(self.nvar+1)]]
        for var in range(1,self.nvar+1):
            constraint=self.weight[:,var]
            if (constraint!=np.zeros((self.nvar,))).any():
                constraint[var]=-1
                tableau.append(constraint)
        self.tableau=np.array(tableau)
        auxiliary=[]
        for idx,bounds in enumerate(self.tableau[1:,0]):
            auxiliary.append([-bounds,-bounds])
            self.tableau[idx][0]=self.nvar+idx
        self.naux=len(auxiliary)
        self.bounds=np.concatenate((self.bounds, np.array(auxiliary)), axis=0)
        pass
    def addBoundInput(self, in_var, lb=-np.inf,ub=np.inf):
        self.inputs.append(in_var)
        self.bounds[in_var]=[lb,ub]
    def pivot(self,old_basic,new_basic):
        col=None
        row=None
        for idx,var in enumerate(self.tableau[0,1:],start=1):
            if var==new_basic:
                col=idx
                self.tableau[0,idx]=old_basic
        for idx,var in enumerate(self.tableau[1:,0],start=1):
            if var==old_basic:
                row=idx
                self.tableau[idx,0]=new_basic
        for idx in range(1,self.nvar):
            if idx==col:
                continue
            self.tableau[row][idx]/=-self.tableau[row][col]
        self.tableau[row][col]=1/self.tableau[row][col]
        pivot_row=self.tableau[row,1:]
        for idx in range(1,self.naux):
            w=self.tableau[idx][col]
            self.tableau[idx][col]=0
            self.tableau[idx,1:]+=w*pivot_row
        pass
    def update(self,var,value):
        if var in self.relu_in:
            self.updateb(var)
    
        pass
    def updateb(self):
        pass
    def updatef(self):
        pass
    def check_relu(self):
        for invar,outvar in zip(self.relu_in,self.relu_out):
            if self.asign[invar]<0 and self.asign[outvar]!=0:
                return 
        pass
    def check_constraints(self):
        pass
    def addWeight(self,in_var,weight,out_var):
        self.weight[in_var][out_var]=weight
        pass
    def tightBounds(self):
        for var in range(1,self.nvar+1):
            if var in self.inputs or var in self.relu_out:
                continue
            bound=[0,0]
            for invar in range(1,self.nvar+1):
                if self.weight[invar][var]>0:
                    bound[0]+=self.weight[invar][var]*self.bounds[invar][0]
                    bound[1]+=self.weight[invar][var]*self.bounds[invar][1]
                elif self.weight[invar][var]<0:
                    bound[1]+=self.weight[invar][var]*self.bounds[invar][0]
                    bound[0]+=self.weight[invar][var]*self.bounds[invar][1]
            self.bounds[var]=bound
        for invar,outvar in zip(self.relu_in,self.relu_out):
            if self.bounds[invar][0]>=0:
                for var in range(1,self.nvar+1):
                    self.weight[invar][var]=self.weight[outvar][var]
                    self.weight[outvar][var]=0
            elif self.bounds[invar][1]<=0:
                for var in range(1,self.nvar+1):
                    self.weight[outvar][var]=0        
    def addReLU(self,in_var,out_var):
        self.relu_in.append(in_var)
        self.relu_out.append(out_var)
        self.relu_timeout.append(1)
        self.bounds[out_var]=[0,np.inf]
    def solve(self):
        self.tightBounds()
        self.setTableau()

