import copy
import random
from Period import Period
import pandas as pd
from Adjustment import Adjustment

'''
Stores an account type and used in the TrialBalance class

'''

class Account:

    # signage: True = debit, False = credit
    '''
    signage: True = debit, False = credit, TRY NOT TO ALTER THIS PARAMETER
    Attributes:
    1. account_name
    2. amount -> ALWAYS USE .getAmount() function when retrieving value from Account object. This will return the value with proper signage in Debit/Credit format
    3. account_period, period of account
    4. currency -> ISO Currency Code
    5. children, parent -> Not currently being used. Use this for some advanced calc logic in future
    6. sign -> default to True.
    7. Adjustments, list of adjustments to the account.

    '''
    def __init__(self, account_name, amount, account_period, currency="USD", sign = True, adjustments = None):

        self.account_name = account_name
        if isinstance(amount,int) or isinstance(amount,float):
            self.amount = amount
        else:
            raise Exception(type(amount),"amount: '"+amount.__str__() + "' must be numeric type")

        if isinstance(account_period,Period):
            self.account_period = account_period
        else:
            raise Exception(self.account_name + ", " +account_period.__str__() + " must be type Period")
        


        self.currency = currency
        self.children = [] # not used in current implementation of tax calculations
        self.parent = None # not used in current implementation of tax calculations
        self.sign = sign

        self.adjustments = adjustments

        if adjustments == None:
            self.adjustments = []
        
    '''
    Used for Generating Trial Balances
    Sets child accounts for hierarchy when generating trial balance
    '''
    def set_child(self,child):

        if isinstance(child,Account):
            self.children.append(child)
            child.parent = self
        else:
            raise Exception(child.__str__() + " must be Account type")


    '''
    The following methods will be used for implementing Trial Balance to Accounts Table Logic.



    def consolidate(self):
        current_amount = self.getAmount()
        children_amount = 0
        for x in self.children:
            children_amount += x.getAmount()
            del x
        self.children = []
        self.amount = children_amount
        return current_amount - children_amount
    

    def remove_all_children(self):
        for x in self.children:
            del x
        self.children = []

    def remove_child(self,account_name):

        for x in self.children:
            if x.account_name == account_name:
                self.children.remove(x)
                del x
                return True
        return False


    def getChildrenValue(self):
        value = 0
        for x in self.children:
            value += x.amount
        return value


    def checkChildren(self):

        if len(self.children) == 0:
            return 0
        else:
            return self.amount - self.getChildrenValue()


    def get_base_account(self):

        current = self

        while current.parent is not None:
            current = current.parent
        
        return current.account_name

    def parse_tree(self):
        to_return = ""
        current = self
        lines = []
        self.__parse_tree_helper(current,lines,0)

        for x in lines:
            to_return += x

        return to_return

    def __parse_tree_helper(self, node, lines, num_tabs):
        
        line = (num_tabs*"\t") + node.account_name + ": " + self.__convert_comma(node.amount) + " " + self.currency +"\n"
        lines.append(line)
        for x in node.children:
            self.__parse_tree_helper(x,lines,num_tabs+1)

    '''

    def __add__(self,other):
        if isinstance(other,int) or isinstance(other, float):
            return self.getAmount() + other

        return self.getAmount() + other.getAmount()
    
    def __sub__(self,other):
        if isinstance(other,int) or isinstance(other, float):
            return self.getAmount() - other
        return self.getAmount() - other.getAmount()
    def __truediv__(self,other):
        if isinstance(other,int) or isinstance(other, float):
            return self.getAmount() / other
        return self.getAmount() / other.getAmount()
    def __mul__(self,other):
        if isinstance(other,int) or isinstance(other, float):
            return self.getAmount() * other
        return self.getAmount() * other.getAmount()
    


    def getAmount(self):

        if self.sign == True:
            return self.amount
        else:
            return self.amount * -1
    

        
    def __convert_comma(self, num):

        return "{:,}".format(num)


    def __str__(self):
        to_return = "Account Name: " + self.account_name + ", Period: " + self.account_period.__str__() + \
                    ", Amount: " + self.__convert_comma(self.amount) + self.currency
        return to_return

    def split_ratio(self, ratio, name_a, name_b):

        to_return = []
        account_a = copy.deepcopy(self)
        account_a.account_name = name_a
        account_a.amount = round(self.amount * float(ratio),2)

        account_b = copy.deepcopy(self)
        account_b.account_name = name_b
        account_b.amount = round(self.amount - account_a.amount,2)
        to_return.append(account_a)
        to_return.append(account_b)

        return to_return

    def split_random(self, new_name="", num_accounts=random.randrange(3, 10)):
        accounts = []
        if self.amount != 0:
            if new_name == "":
                new_name = self.account_name
            print(new_name)
            total_amount = self.amount
            

            base_amount = total_amount/num_accounts
            current_sum = 0
            for i in range(0, num_accounts-1):
                new_account = copy.deepcopy(self)
                new_account.amount = round(base_amount * random.random())
                current_sum += new_account.amount
                new_account.account_name = new_name + str(i)
                accounts.append(new_account)

            plug_account = copy.deepcopy(self)
            plug_account.amount = total_amount - current_sum
            plug_account.account_name = new_name + str(num_accounts)
            accounts.append(plug_account)

        return accounts

    def convert_shadow_account(self,account_collection = "TBFC", account_class = "", account_data_type = ""):
        to_convert = ShadowAccount(self.account_name,self.getAmount(),self.account_period,self.currency,self.sign,account_collection,account_class,account_data_type)
        return to_convert

    def get_adjustment_amount(self,colct,adj_cls,adj_type,pd):
        adj = Adjustment(0,adj_class=adj_cls,adj_collection=colct,adj_type=adj_type,adj_period=pd)
        for x in self.adjustments:
            if x.apply_adj(adj) == True:
                # print("apply this adj")
                # print(x) 
                return x.adj_amount
        return 0



class ShadowAccount(Account):

    def __init__(self, account_name, amount, account_period, currency="USD", sign = True, account_collection = "TBFC", account_class = "", account_data_type = "", adjustment = None):
        self.__account_list = self.__import__account_list()
        
        if account_name not in self.__account_list:
            raise Exception("'" + account_name + "'" + " is not a valid account")

        Account.__init__(self,account_name, amount, account_period, currency="USD", sign = True)
        self.account_collection = account_collection
        self.account_class = account_class
        self.account_data_type = account_data_type
        self.adjustment = adjustment
        self.post_fix_children = []

    def __eq__(self, other):
        if isinstance(other,ShadowAccount):
            return (self.account_name,self.account_class,self.account_collection,self.account_period,self.account_data_type) == (other.account_name,other.account_class,other.account_collection,other.account_period,other.account_data_type)
        return False
    def __import__account_list(self):
        df = pd.read_csv("config//shadow_accounts.csv")
        return df["Account Types"].to_numpy()
    
    def __str__(self):
        to_return = self.account_name + ",\t" + self.account_collection +",\t" + self.currency + ",\t" + self.account_class +",\t" + str(self.amount) + ",\t" + self.account_period.period_type+str(self.account_period.period_year)

        return to_return

    '''
    Not used in current implementation of calculation
    '''
    
    def has_children(self):
        if len(self.children)>0:
            return True
        else:
            return False
    
    '''
    Not used in current implementation of calculation
    '''
    def set_child(self,child):
    
        self.children.append(child)
        if isinstance(child, Account):
            child.parent = self


    '''
    Not used in current implementation of calculation
    '''
    def to_post_fix(self):

        if self.has_children() == True:
            operators = set(['+', '-', '*', '/', '(', ')', '^'])
            priority = {'+':1, '-':1, '*':2, '/':2, '^':3}
            stack = []
            output = []

            for c in self.children:
                if c not in operators:
                    output.append(c)
                elif c == '(':
                    stack.append('(')
                elif c == ')':
                    while stack and stack[-1]!='(':
                        output.append(stack.pop())
                    stack.pop()
                else:
                    while stack and stack[-1]!='(' and priority[c]<=priority[stack[-1]]:
            
                        output+=stack.pop()

                    stack.append(c)
            while stack:
                output+=stack.pop()

            self.post_fix_children = output
        
    '''
    Not used in current implementation of calculation
    '''
    def compile_post_fix(self):

        if self.has_children() == True:
            self.to_post_fix()
            stack = []
            # print(self.post_fix_children)
            for x in self.post_fix_children:
                if isinstance(x,ShadowAccount):
                    stack.append(x)
                    
                else:
                    a = stack.pop()
                    b = stack.pop()
                    if isinstance(a,Account):
                        a = a.getAmount()
                    if isinstance(b,Account):
                        b = b.getAmount()
                    if x == '+':
                        stack.append(b + a)
                    elif x == '-':
                        stack.append(b - a)
                    elif x == '*':
                        stack.append(b * a)
                    elif x == '/':
                        stack.append(b / a)
            
            self.amount = stack.pop()






# p = Period("CYE","2022", "01-01-2022", "12-31-2022")
# a = ShadowAccount("Interest Income (Third Party)", 0.00, p)
