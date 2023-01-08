from Entity import Entity, DRE
from USSH import USSH
from CFC import CFC
import copy
import pandas as pd
from Account import ShadowAccount
from Adjustment import Adjustment

class OrgChart:
    # 
    def __init__(self, period):
        self.period = period
        self.parents = []
    
    def find_entity(self, entity):
        for x in self.parents:
            results = x.search_all_children(entity)
            if results is not None:
                return results
        return None
    def add_parent(self,parent):
        self.parents.append(parent)
    def get_all_entities(self):
        results = []
        for x in self.parents:
            results.append(x)
            results.extend(self.get_all_children(x))
        return results
    def get_all_children(self,entity):
        results = []
        self.__get_all_children_helper(entity,results)
        return results
    def __get_all_children_helper(self, entity, results):
        if len(entity.children) == 0:
            results.append(entity)
        else:
            for x in entity.children:
                self.__get_all_children_helper(x, results)

    # VALIDATE PERIOD
    def import_entities(self,things_tbl_fName):
        things_df = pd.read_csv(things_tbl_fName)
        
        for index, row in things_df.iterrows():

            if row['Type'] == "USSH":
                self.add_parent(USSH(row['Thing'],row['Country'],row['ISO Currency Code'],self.period,row['Type']))
            elif row['Type'] == "CFC":
                self.add_parent(CFC(row['Thing'],row['Country'],row['ISO Currency Code'],self.period,row['Type']))
            else:
                raise Exception(row['Type'] + " is not a valid type!")

    def import_relationships(self,rel_tbl_fName):
        rel_df = pd.read_csv(rel_tbl_fName)
        
        if len(self.parents) == 0:
            raise Exception("Must import Things table first!")

        for index, row in rel_df.iterrows():
            new_parent = self.find_entity(row['Parent'])
            new_child = self.find_entity(row['Child'])
            if new_parent == None:
                raise Exception(row['Parent'] + " was not defined in Things Table")
            if new_child == None:
                raise Exception(row['Child'] + " was not defined in Things Table")
            
            if self.find_entity(new_parent) == None:
                new_parent.set_child(new_child,float(row["Ownership Percentage"]))
                self.add_parent(new_parent)
            else:
                self.find_entity(new_parent).set_child(new_child,float(row["Ownership Percentage"]))
        
        new_parents = []
        for x in self.parents:
            if len(x.parents) == 0:
                new_parents.append(x)
        self.parents = new_parents
    def calculate(self):
        
        for x in self.parents:
            x.calculate()
    

    def roll_forward(self,keep_accounts = False):
        next_year_org_chart = copy.deepcopy(self)

        if keep_accounts == False:
            for x in next_year_org_chart.entities:
                x.clear_accounts()

        return next_year_org_chart
    
    def __str__(self):
        to_return = ""
        for x in self.parents:
            lines = []
            self.__print_helper(x,0,lines)
            for x in lines:
                to_return += x + "\n"
        return to_return
    def __print_helper(self,entity, indent,lines):
        lines.append(indent*"\t" + entity.name + ": " + entity.type + ", Accounts = " +str(entity.get_accounts_table().num_active_accounts()) + ", Adjustments = " + str(entity.get_accounts_table().num_active_adjustments()))
        for x in entity.children:
            self.__print_helper(x,indent+1,lines)

    # EXTREMELY INEFFICIENT
    # MAKE IT SO YOU CAN IMPORT ADJUSTMENTS TABLE FIRST AND IT STILL WORKS ()
    # PERIOD VALIDATION
    def import_accounts(self,acc_tbl_name):
        acc_df = pd.read_csv(acc_tbl_name)
        entities = []
        entities = set(entities)
        unmatched_entity = []
        for index, row in acc_df.iterrows():
            e = row['Entity']
            entity = self.find_entity(e)
            if entity == None:
                unmatched_entity.append(e)
            else:
                acc_tbl = entity.get_accounts_table()
                acc_name = str(row['Account Name'])
                a = acc_tbl[acc_name]
                
                a.amount = float(row['Amount'])
                a.currency = row['ISO Currency Code']
                # print(self.period)
                a.account_period = self.period
                a.account_collection = str(row['Collection'])
                a.account_class = str(row['Class'])
                a.account_data_type = str(row['Data Type'])
                
        
        if len(unmatched_entity) > 0:
            raise Exception(unmatched_entity.__str__() + " are not valid entities!")
    
    # EXTREMELY INEFFICIENT
    # PERIOD VALIDATION
    def import_adjustments(self, adj_tbl_name):

        unmatched_entity = []
        adj_df = pd.read_csv(adj_tbl_name)

        for index, row in adj_df.iterrows():
            entity = self.find_entity(row['Entity'])
            acc_tbl = entity.get_accounts_table()
            acc_tbl.period = self.period
            
            # print("entity: " + entity.__str__() +", account name:  "+row['Account Name'])
            a = acc_tbl[row['Account Name']]
            adj_amount = float(row['Adjustment Amount'])
            adj_col = str(row['Adjustment Collection'])
            adj_type = str(row['Adjustment Type'])
            adj_curr = str(row['ISO Currency Code'])
            adj_perc = float(row['Adjustment Percentage'])
            adj_class = str(row['Adjustment Class'])
            adj_curr = str(row['ISO Currency Code'])
            # print(self.period)
            adj = Adjustment(adj_amount=adj_amount,adj_class=adj_class,adj_collection=adj_col,adj_period=self.period,adj_type=adj_type,adj_perc=adj_perc,currency = adj_curr)
            # print(adj)
            a.adjustments.append(adj)
    def pull_outputs_csv(self, fName):
        acc_df = pd.DataFrame({
            'Account Name': pd.Series(dtype='str'),
            'Amount': pd.Series(dtype='float'),
            'ISO Currency Code': pd.Series(dtype='str'),
            'Period': pd.Series(dtype='str'),
            'Collection': pd.Series(dtype='str'),
            'Class': pd.Series(dtype='str'),
            'Data Type': pd.Series(dtype='float')})
        for x in self.parents:
            acc_df = pd.concat([acc_df,x.pull_consol_ouput_accounts_df()])
        
        acc_df.to_csv(fName)
        print("file saved to " + fName)