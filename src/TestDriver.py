from Account import Account,Adjustment,ShadowAccount
from AccountsTable import AccountsTable
from Trialbalance import TrialBalance
from Period import Period
from Entity import Entity
import pandas as pd
import random

names = []

p = Period("CYE",2022, "01-01-2022", "12-31-2022")
ussh = Entity(name="USSH",country="US",currency = "USD",period=p,entity_type="USSH")
ownership_percs = []
tickers = []
fileRead = open('files//Testing//CompanyNames.txt', "r")

for line in fileRead:
    names.append(line.strip())
fileRead.close()


for x in range(0,10):
    ownership_percs.append(1)
for x in range(0,5):
    ownership_percs.append(random.random())

fileRead = open('files//Testing//StockTickers.txt', "r")
for line in fileRead:
    tickers.append(line.strip())
fileRead.close()

print(ussh)
for x in range(0,15):
    
    t = TrialBalance(p)
    print(tickers[x])
    t.generate_random_tb(starting_asset=100000,ticker=tickers[x])
    a = AccountsTable()
    a.pull_tb(t)
    a.generate_random_adjustments(["OtherDeductions"])
    a.print_adj()
    e = Entity(name = names[x], country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
    a.export_adjustments("tests//USSH_GILTI//"+e.name+"_adjustments.csv")
    a.export("tests//USSH_GILTI//"+e.name+"_accounts.csv")
    ussh.set_child(e,ownership_percs[x])
    print(e)
