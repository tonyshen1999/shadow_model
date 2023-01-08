from Entity import Entity, DRE
from USSH import USSH
from CFC import CFC
import copy
import pandas as pd
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
    def import_entities(self,things_tbl_fName):
        things_df = pd.read_csv(things_tbl_fName)
        things_list = OrgChart(self.period)
        for index, row in things_df.iterrows():
            if row['Type'] == "USSH":
                things_list.add_parent(USSH(row['Thing'],row['Country'],row['ISO Currency Code'],row['Period'],row['Type']))
            elif row['Type'] == "CFC":
                things_list.add_parent(CFC(row['Thing'],row['Country'],row['ISO Currency Code'],row['Period'],row['Type']))
            else:
                raise Exception(row['Type'] + " is not a valid type!")
        return things_list
    def import_relationships(self,things_tbl_fName,rel_tbl_fName):
        rel_df = pd.read_csv(rel_tbl_fName)
        things_list = self.import_entities(things_tbl_fName)

        for index, row in rel_df.iterrows():
            new_parent = things_list.find_entity(row['Parent'])
            new_child = things_list.find_entity(row['Child'])
            if new_parent == None:
                raise Exception(row['Parent'] + " was not defined in Things Table")
            if new_child == None:
                raise Exception(row['Child'] + " was not defined in Things Table")
            
            if self.find_entity(new_parent) == None:
                new_parent.set_child(new_child,float(row["Ownership Percentage"]))
                self.add_parent(new_parent)
            else:
                self.find_entity(new_parent).set_child(new_child,float(row["Ownership Percentage"]))
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
        lines.append(indent*"\t" + entity.name + ": " + entity.type)
        for x in entity.children:
            self.__print_helper(x,indent+1,lines)
