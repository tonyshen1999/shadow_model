from Account import Account,Adjustment,ShadowAccount
from AccountsTable import AccountsTable
from Trialbalance import TrialBalance
from Period import Period
from Entity import Entity, CFC, USSH
import pandas as pd
import random
import os
from CalcScript import CFCTestedIncome,USSH951AInclusion
from Attributes import AttributesTable,Attribute


def generate_csv(p,info_file_name,output_dir):

    entity_info_df = pd.read_csv(info_file_name)

    # names = []

    ussh = USSH(name="USSH",country="US",currency = "USD",period=p,entity_type="USSH")
    # ownership_percs = []
    # tickers = []

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

    # fileRead = open('files//Testing//CompanyNames.txt', "r")

    # for line in fileRead:
    #     names.append(line.strip())
    # fileRead.close()


    # fileRead = open('files//Testing//StockTickers.txt', "r")
    # for line in fileRead:
    #     tickers.append(line.strip())
    # fileRead.close()

    print(ussh)
    for index, row in entity_info_df.iterrows():
        
        t = TrialBalance(p)
        print(row["Tickers"])
        t.generate_random_tb(starting_asset=1000000,ticker=row["Tickers"])
        a = AccountsTable()
        a.pull_tb(t)
        if bool(row["Income or Loss"]) == False:
            a.convert_loss()
        if bool(row["163j"]) == True:
            a.force163j()
        a.generate_random_adjustments(["OtherDeductions"])
        a.print_adj()
        e = CFC(name = row["Entity Names"], country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
        a.export_adjustments(output_dir+e.name+"_adjustments.csv")
        a.export(output_dir+e.name+"_accounts.csv")
        x_acc_df = a.get_accounts_df()
        x_acc_df.insert(0,'Entity',e.name)
        acc_df = pd.concat([acc_df,x_acc_df])
        x_adj_df = a.get_adjustments_df()
        x_adj_df.insert(0,'Entity',e.name)
        adj_df = pd.concat([adj_df,x_adj_df])
        # ussh.set_child(e,float(row["Ownership Percentage"]))
        print(e)
    acc_df.to_csv(output_dir+"combined_accounts_table.csv")
    adj_df.to_csv(output_dir+"combined_adjustments_table.csv")

def import_data(save_file,comp_name_file,ticker_file,num_entities):

    names = []
    tickers = []
    fileRead = open(comp_name_file, "r")

    for line in fileRead:
        names.append(line.strip())
    fileRead.close()

    fileRead = open(ticker_file, "r")
    for line in fileRead:
        tickers.append(line.strip())
    fileRead.close()
    
    entity_names = []
    entity_tickers = []
    entity_perc = []
    entity_income_loss = []
    entity_163j = []
    for x in range(0,num_entities):
        entity_names.append(names[x])
        entity_tickers.append(tickers[x])
        
        if random.randrange(0, 10)%2==0:
            entity_perc.append(round(random.uniform(.01,.99),4))
        else:
            entity_perc.append(1.0)
        if bool(random.getrandbits(1)):
            entity_income_loss.append(True)
        else:
            entity_income_loss.append(False)
        if random.randrange(0, 10)%4==0:
            entity_163j.append(True)
        else:
            entity_163j.append(False)
    
    entity_info_df = pd.DataFrame({
        "Entity Names":entity_names,
        "Tickers":entity_tickers,
        "Ownership Percentage":entity_perc,
        "Income or Loss": entity_income_loss,
        "163j": entity_163j
    })
    print(entity_info_df)
    entity_info_df.to_csv(save_file)
def pull_accounts(ussh, fName):
    acc_df = pd.DataFrame({
        'Account Name': pd.Series(dtype='str'),
        'Amount': pd.Series(dtype='float'),
        'ISO Currency Code': pd.Series(dtype='str'),
        'Period': pd.Series(dtype='str'),
        'Collection': pd.Series(dtype='str'),
        'Class': pd.Series(dtype='str'),
        'Data Type': pd.Series(dtype='float')})

    x_acc_df = ussh.get_accounts_table().get_accounts_df()
    x_acc_df.insert(0,'Entity',ussh.name)
    acc_df = pd.concat([acc_df,x_acc_df])

    for x in ussh.children:
        x_acc_df = x.get_accounts_table().get_accounts_df()
        x_acc_df.insert(0,'Entity',x.name)
        acc_df = pd.concat([acc_df,x_acc_df])
    
    acc_df.to_csv(fName)

def read_csv(p,ussh,dir_path,ownership_dict):

    
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
        if "accounts" in x and "combined" not in x:
            print(x)
            a.import_accounts(dir_path+"//"+x)
            e = CFC(name = e_name, country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
            ussh.set_child(e,ownership_dict[e_name])
            print(e.get_accounts_table())
        # del x
    
    for x in res:
        if "adjustments" in x and "combined" not in x:
            e_name = x.split("_")[0]
            e = ussh[e_name]
            # print(x)
            e.get_accounts_table().import_adjustments(dir_path+"//"+x)
    
def import_ownership(info_file_name):

    entity_info_df = pd.read_csv(info_file_name)
    ownership_dict = {}
    for index, row in entity_info_df.iterrows():
        ownership_dict[row["Entity Names"]] = float(row["Ownership Percentage"])
    return ownership_dict


print(import_data('tests//USSH_GILTI//EntityConfigFile.csv','files//Testing//CompanyNames.txt','files//Testing//StockTickers.txt',15))

p = Period("CYE",2022, "01-01-2022", "12-31-2022")
ussh = USSH(name="USSH",country="US",currency = "USD",period=p,entity_type="USSH")
ownership_dict = import_ownership("tests//USSH_GILTI//EntityConfigFile.csv")
generate_csv(p,"tests//USSH_GILTI//EntityConfigFile.csv","tests//USSH_GILTI//Entity_Files_v3//")
read_csv(p,ussh,"tests//USSH_GILTI//Entity_Files_v3",ownership_dict)

atr = AttributesTable(p,"CFCAttributes.csv")

for x in ussh.children:
    x.calculate()

ussh.calculate()
ctr = 1
for x in ussh.children:
    print(str(ctr) + ":----------")
    print(x)
    print("----------ACCOUNTS-----------")
    print(x.get_accounts_table())
    print("----------ADJUSTMENTS-----------")
    print(x.get_accounts_table().print_adj())
    ctr +=1

pull_accounts(ussh,"tests//USSH_GILTI//accounts_output.csv")