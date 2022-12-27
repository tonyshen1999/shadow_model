import pandas as pd
from Account import Account,ShadowAccount
# Turn attributestable into a set. Figure out hashing in Python lol

class AttributesTable:
    def __init__(self, period, fName):
        
        self.period = period
        self.attributes = []
        # self.attributes = set(self.attributes)
        
        self.add_atr("DefaultAttributes.csv")
        
        self.add_atr(fName)

    def add_atr(self, fName):
        atr_df = pd.read_csv("Attributes//"+fName)
        for index, row in atr_df.iterrows():
            atr = Attribute(atr_name=row["AttributeName"],atr_value=row["AttributeValue"],atr_begin=row["AttributeStartDate"],atr_end=row["AttributeEndDate"])
            self.attributes.append(atr)
    
    def __str__(self):
        to_return = ""
        for x in self.attributes:
            to_return += x.__str__() + "\n"
        return to_return
    def __getitem__(self,key):
        
        if isinstance(key,str):
            search = Attribute(key,"","","")
            for x in self.attributes:
                if x == search:
                    return x
    def pull_account_atr(self):
        accounts = []
        for x in self.attributes:
            val = x.atr_value

            if isinstance(val,str) and val.replace("-","").replace(".","").isnumeric():
                name = "[" + x.atr_name + "]"
                a = ShadowAccount(name,float(x.atr_value),self.period)
                accounts.append(a)

        return accounts
    
class Attribute:
    def __init__(self, atr_name,atr_value,atr_begin,atr_end=""):
        self.atr_name = atr_name
        if isinstance(atr_value, str):
            if atr_value == "Yes":
                atr_value = True
            elif atr_value == "No":
                atr_value = False
        self.atr_value = atr_value
        self.atr_beg = atr_begin
        self.atr_end = atr_end
    def __str__(self):
        to_return = self.atr_name + ": " + str(self.atr_value) + ", begin: " + str(self.atr_beg) + ", end:" + str(self.atr_end)

        return to_return

    def __eq__(self,other):
        if isinstance(other,Attribute):
            return (self.atr_name) == (other.atr_name)
        return False
    
# atr = AttributesTable("CFCAttributes.csv")
# print(atr["USTaxRate"])
# # print(atr)