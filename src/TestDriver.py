from Account import Account,Adjustment,ShadowAccount
from AccountsTable import AccountsTable
from Trialbalance import TrialBalance
from Period import Period
from Entity import Entity
import pandas as pd
import random
import os

def generate_csv(p):
    names = []

    
    ussh = Entity(name="USSH",country="US",currency = "USD",period=p,entity_type="USSH")
    ownership_percs = []
    tickers = []

    acc_df = pd.DataFrame({
        'Account Name': pd.Series(dtype='str'),
        'Amount': pd.Series(dtype='float'),
        'ISO Currency Code': pd.Series(dtype='str'),
        'Period': pd.Series(dtype='str'),
        'Collection': pd.Series(dtype='str'),
        'Class': pd.Series(dtype='str'),
        'Data Type': pd.Series(dtype='float')})
    adj_df = pd.DataFrame({
        'Account Name': pd.Series(dtype='str'),
        'Adjustment Type': pd.Series(dtype='float'),
        'Adjustment Collection': pd.Series(dtype='str'),
        'Adjustment Class': pd.Series(dtype='str'),
        'Adjustment Amount': pd.Series(dtype='str'),
        'ISO Currency Code': pd.Series(dtype='str'),
        'Adjustment Period': pd.Series(dtype='float'),
        'Adjustment Percentage': pd.Series(dtype='str')})

    fileRead = open('files//Testing//CompanyNames.txt', "r")

    for line in fileRead:
        names.append(line.strip())
    fileRead.close()


    fileRead = open('files//Testing//StockTickers.txt', "r")
    for line in fileRead:
        tickers.append(line.strip())
    fileRead.close()

    print(ussh)
    for x in range(0,15):
        
        t = TrialBalance(p)
        print(tickers[x])
        t.generate_random_tb(starting_asset=1000000,ticker=tickers[x])
        a = AccountsTable()
        a.pull_tb(t)
        a.generate_random_adjustments(["OtherDeductions"])
        a.print_adj()
        e = Entity(name = names[x], country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
        a.export_adjustments("tests//USSH_GILTI//Entity_Files//"+e.name+"_adjustments.csv")
        a.export("tests//USSH_GILTI//Entity_Files//"+e.name+"_accounts.csv")
        x_acc_df = a.get_accounts_df()
        x_acc_df.insert(0,'Entity',e.name)
        acc_df = pd.concat([acc_df,x_acc_df])
        x_adj_df = a.get_adjustments_df()
        x_adj_df.insert(0,'Entity',e.name)
        adj_df = pd.concat([adj_df,x_adj_df])
        # ussh.set_child(e,ownership_percs[x])
        print(e)
    acc_df.to_csv("tests//USSH_GILTI//combined_accounts_table.csv")
    adj_df.to_csv("tests//USSH_GILTI//combined_adjustments_table.csv")




def read_csv(p,ussh):

    dir_path = "tests//USSH_GILTI//Entity_Files"
    # ownership_percs = []
    # for x in range(0,10):
    #     ownership_percs.append(1)
    # for x in range(0,5):
    #     ownership_percs.append(random.random())
    # list file and directories
    res = os.listdir(dir_path)
    for x in res:
        e_name = x.split("_")[0]
        
        a = AccountsTable()
        if "accounts" in x:
            # print(x)
            a.import_accounts(dir_path+"//"+x)
            e = Entity(name = e_name, country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
            ussh.set_child(e,1)
        # del x
    
    for x in res:
        if "adjustments" in x:
            e_name = x.split("_")[0]
            e = ussh[e_name]
            # print(x)
            e.get_accounts_table().import_adjustments(dir_path+"//"+x)
    


p = Period("CYE",2022, "01-01-2022", "12-31-2022")
ussh = Entity(name="USSH",country="US",currency = "USD",period=p,entity_type="USSH")
generate_csv(p)
read_csv(p,ussh)
ctr = 1
for x in ussh.children:
    print(str(ctr) + ":---------")
    print(x)
    print("----------ACCOUNTS-----------")
    print(x.get_accounts_table())
    print("----------ADJUSTMENTS-----------")
    print(x.get_accounts_table().print_adj())
    ctr +=1

