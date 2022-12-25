import copy
import random

class Account:

    # signage: True = debit, False = credit
    def __init__(self, account_name, amount, account_period, currency="USD", sign = True):
        self.account_name = account_name
        self.amount = amount
        self.account_period = account_period
        self.currency = currency
        self.children = []
        self.parent = None
        self.sign = sign

        
    
    def set_child(self,child):

        self.children.append(child)
        child.parent = self
    
    def consolidate(self):

        if len(self.children) > 0:
            self.amount = self.getChildrenValue()
        
    def getAmount(self):

        if self.sign == True:
            return self.amount
        else:
            return self.amount * -1
    
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
