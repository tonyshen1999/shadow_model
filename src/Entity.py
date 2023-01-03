from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
import pandas as pd
import copy
import itertools
from Attributes import AttributesTable,Attribute

class Entity:

    id_obj = itertools.count()
    
    # Create an Attributes Class for each Entity type (CFC, DRE, USSH). Load Attributes pushes appropriate attribute type based on Entity type
    #
    def __init__(self, name,country, currency, period, entity_type="", tb = None, accounts_table = None,atr_tb = None):

        self.id = next(Entity.id_obj)
        self.name = name
        self.country = country
        self.type = ""
        self.currency = currency
        self.period = period

        self.children = {}
        self.parents = {}
        
        self._accounts_table = accounts_table
        self.atr_tb = atr_tb

        if self.atr_tb == None:
            self.atr_tb = AttributesTable(self.period)

        # if tb == None:
        #     self.__tb = TrialBalance(self.period,currency=self.currency)
        # else:
        #     self.__tb = tb
        
        if self._accounts_table == None:
            self.__tb = TrialBalance(self.period,currency=self.currency)
            self._accounts_table = AccountsTable()
            self._accounts_table.pull_tb(self.__tb)
    def __str__(self):
        # parent = self.parent
        # if parent == None:
        #     parent = "None"
        # else:
        #     parent = parent.name
        to_return = "ID: " + str(self.id) + ", Name: " + self.name + ", Type: " + self.type + ", Country: " + self.country #+ ", Parent: " + parent +", Percent Owned: " + str(self.percent_owned*100) + "%"
        return to_return
    def get_accounts_table(self):
        return self._accounts_table
    def set_accounts_table(self,acc_tbl):
        self._accounts_table = acc_tbl
    def get_tb(self):
        return self.__tb
    def set_tb(self,tb):
        self.__tb = tb
    def set_child(self,child, percent_owned):
        self.children[child] = percent_owned
        child.parents[self] = percent_owned
    def __eq__(self,other):
        return (self.name,self.type) == (other.name,other.type)
    def __hash__(self):
        return hash(self.name) ^ hash(self.type)
    def __getitem__(self,key):
        
        for x in self.children.keys():
            if x.name == key:
                return x
        
        to_return = copy.deepcopy(self)
        to_return.name = key
        print("*****WARNING*****\n" + key + " DOES NOT EXIST")
        return to_return

    def pull_accounts_csv(self, fName):
        
        entity = []
        account_names = []
        account_amount = []
        account_currency = []
        account_collection = []
        account_class = []
        account_data_type = []
        account_period = []

        for x in self._accounts_table.accounts:
            entity.append(self.name)
            account_names.append(x.account_name)
            account_amount.append(x.getAmount())
            account_currency.append(x.currency)
            account_collection.append(x.account_collection)
            account_class.append(x.account_class)
            account_data_type.append(x.account_data_type)
            account_period.append(x.account_period.period_type + str(x.account_period.period_year))
        
        accounts_dict = {
            "Entity":entity,
            "Account Name":account_names,
            "Amount":account_amount,
            "ISO Currency Code":account_currency,
            "Period":account_period,
            "Collection":account_collection,
            "Class":account_class,
            "Data Type":account_data_type
        }

        df = pd.DataFrame(accounts_dict)
        df.to_csv(fName)

    def contains_account(self,acc_name):
        for x in self._accounts_table:
            if x.account_name == acc_name:
                return True

        return False
    
    def _create_account(self,acc_name,amt = 0,collection = ""):
        a = ShadowAccount(account_name=acc_name,amount = amt, account_period=self.period,currency=self.currency,account_collection=collection)
        return a

    def EBIT(self):
        if self.contains_account("EBIT") == False:
            a = self._create_account("EBIT")

            amount = (self._accounts_table["Sales"].getAmount()+self._accounts_table["COGS"].getAmount()+self._accounts_table["OtherIncomeThirdParty"].getAmount()
            +self._accounts_table["OtherIncomeIntercompany"].getAmount()+self._accounts_table["SGA"].getAmount()+self._accounts_table["OtherDeductions"].getAmount()
            +self._accounts_table["DividendIncome"].getAmount()+self._accounts_table["NonIncomeTaxes"].getAmount()+self._accounts_table["Depreciation"].getAmount()+self._accounts_table["Amortization"].getAmount()+self._accounts_table["InterestIncomeIntercompany"].getAmount()+self._accounts_table["InterestExpenseIntercompany"].getAmount())
            a.amount = amount

            a.account_collection = "EBIT"
            self._accounts_table.add_account(a)

    def EBIT_TI(self):
        if self.contains_account("TI_EBIT") == False:
            a = self._create_account("TI_EBIT")
            self.EBIT()
            # Apply M-1 Adjustments for Taxable Income EBIT
            self._accounts_table.apply_adjustments(acct_name="M1Adjustments",acct_colct="ForeignSchM-1Adj",adj_colct="",adj_cls="ForeignSchM-1Adj",adj_type="ForeignSchM-1Adj",pd=self.period,currency = "USD")

            amount = (self._accounts_table["EBIT"]+ self._accounts_table["M1Adjustments"].getAmount())
            a.amount = amount

            a.account_collection = "TI_EBIT"
            self._accounts_table.add_account(a)
    def sec163j(self):
        if self.contains_account("TI_EBIT") == False:
            colct = "Sec163j"
            self.EBIT_TI()

            ebit_amount = self._accounts_table["EBIT"] 

            ati = self._create_account("ATI",(ebit_amount-self._accounts_table["Depreciation"].getAmount()-self._accounts_table["Amortization"].getAmount()+self._accounts_table["M1Adjustments"].getAmount()))
            ati.account_collection = colct
            self._accounts_table.add_account(ati)

            
            
            sec163_lim_amt = -1*(min(ati.getAmount()*self.atr_tb["163jLimit_Perc"].get_value(),0)+self._accounts_table["InterestIncomeThirdParty"].getAmount())
            sec163_limitation = self._create_account("Section163jLimitation", sec163_lim_amt)
            sec163_limitation.account_collection = colct
            self._accounts_table.add_account(sec163_limitation)

            py_disallowed_amt = self._accounts_table.search_period(self.period-1)["Sec163DisallowedInterestExpense"].getAmount()
            

            int_exp_util_amt = self._accounts_table["InterestExpenseThirdParty"].getAmount() + py_disallowed_amt
            int_exp_util_amt = min(int_exp_util_amt,sec163_lim_amt)
            int_exp_util = self._create_account("InterestExpenseUtilized",int_exp_util_amt)
            int_exp_util.account_collection = colct
            
            disallowed_int_exp = self._create_account("Sec163DisallowedInterestExpense",(self._accounts_table["InterestExpenseThirdParty"].getAmount()-int_exp_util_amt))
            disallowed_int_exp.account_collection = colct
            self._accounts_table.add_account(int_exp_util)
            self._accounts_table.add_account(disallowed_int_exp)

    def calculate(self):
        self.sec163j()

class CFC(Entity):
    def __init__(self, name,country, currency, period, entity_type="", tb = None, accounts_table = None,atr_tb = None):
        atr = AttributesTable(period,"CFCAttributes.csv")
        super().__init__(name=name,country=country, currency=currency, period=period, entity_type="CFC", tb=tb, accounts_table=accounts_table,atr_tb = atr)
    def calculate(self):
        self.CFCTestedIncome()

    def CFCTestedIncome(self):
        if self.contains_account("TentativeTestedIncomeBeforeTaxes") == False:
            self.sec163j()
            tent_tested_income_amt = self._accounts_table["TI_EBIT"].getAmount()+self._accounts_table["InterestExpenseUtilized"].getAmount()+self._accounts_table["InterestIncomeThirdParty"].getAmount()-self._accounts_table["SubpartF_Income"].getAmount()

            tent_tested_income = self._create_account("TentativeTestedIncomeBeforeTaxes",tent_tested_income_amt)
            colct = "TestedIncome"
            tent_tested_income.account_collection=colct
            self._accounts_table.add_account(tent_tested_income)

            tested_income_etr_amt = self._accounts_table["IncomeTaxes"]/tent_tested_income_amt
            hte = self.atr_tb["Section951AHighTaxElection"].atr_value
            tested_income = self._create_account("TestedIncome",0)
            tested_loss = self._create_account("TestedLoss",0)
            tested_income.account_collection = colct
            tested_loss.account_collection = colct

            hte_met = (tested_income_etr_amt*-1) > (self.atr_tb["HTETaxPercentage"].get_value()*self.atr_tb["USTaxRate"].get_value())
            # print(tested_income_etr_amt)

            if hte == False or hte_met == False:
                if tent_tested_income_amt > 0:
                    tested_loss.amount = tent_tested_income_amt
                    tested_income.amount = 0
                else:
                    tested_income.amount = tent_tested_income_amt
                    tested_loss.amount = 0
            self._accounts_table.add_account(tested_income)
            self._accounts_table.add_account(tested_loss)

            # pro_rata_tested_income = self._create_account("ProRataTestedIncome",tested_income.getAmount() * self.ownership)
            # pro_rata_tested_loss = self._create_account("ProRataTestedLoss",tested_loss.getAmount() * self.ownership)

            # pro_rata_tested_income.account_collection=colct
            # pro_rata_tested_loss.account_collection=colct

            # self.accounts_tbl.add_account(pro_rata_tested_income)
            # self.accounts_tbl.add_account(pro_rata_tested_loss)


            qbai_amount = 0
            if tested_income.getAmount() <0 and hte_met == False:
                qbai_amount = self._accounts_table["QBAI"].getAmount()
            tested_income_qbai = self._create_account("TestedIncomeQBAI",qbai_amount)
            tested_income_qbai.account_collection=colct
            self._accounts_table.add_account(tested_income_qbai)
            

            tested_loss_qbai_amt = 0
            if tested_loss.getAmount()>0:
                tested_loss_qbai_amt = self._accounts_table["QBAI"].getAmount()*self.atr_tb["TestedLossQBAIAmount"].get_value()
            tested_loss_qbai = self._create_account("TestedLossQBAI",tested_loss_qbai_amt)
            tested_loss_qbai.account_collection=colct
            
            self._accounts_table.add_account(tested_loss_qbai)
            
            
            etr = self._create_account("TestedIncome_ETR",tested_income_etr_amt*-1)
            etr.account_collection = colct
            self._accounts_table.add_account(etr)

            tested_interest_expense_amt = self._accounts_table["InterestExpenseUtilized"].getAmount()
            tested_interest_income_amt = self._accounts_table["InterestIncomeThirdParty"].getAmount()
            # print(hte_met)
            if hte_met == True:
                
                tested_interest_expense_amt = 0
                tested_interest_income_amt = 0

            tested_interest_expense_amt = max(tested_interest_expense_amt-tested_loss_qbai_amt,0)

            tested_interest_income = self._create_account("TestedInterestIncome",tested_interest_income_amt)
            tested_interest_expense = self._create_account("TestedInterestExpense",tested_interest_expense_amt)
            
            tested_interest_income.account_collection=colct
            tested_interest_expense.account_collection=colct
            

            self._accounts_table.add_account(tested_interest_expense)
            self._accounts_table.add_account(tested_interest_income)
            
            tested_income_taxes_amt = self._accounts_table["IncomeTaxes"].getAmount()
            
            if hte_met:
                tested_income_taxes_amt = 0
            
            tested_income_taxes = self._create_account("TestedIncomeTaxes",tested_income_taxes_amt)
            tested_income_taxes.account_collection = colct

            self._accounts_table.add_account(tested_income_taxes)

class DRE(Entity):
    def calculate(self):
        pass

class USSH(Entity):
    def calculate(self):
        self.USSH951A()
    def USSH951A(self):
        cfcs = self.children
        cfc_atr = AttributesTable(self.period,"CFCAttributes.csv")
        # ussh_atr = AttributesTable(self.period)
        agg_cfc_tested_income_amt = 0
        agg_cfc_tested_loss_amt = 0
        qbai_amt = 0
        agg_tested_interest_inc_amt = 0
        agg_tested_interest_exp_amt = 0
        agg_tested_income_tax_amt = 0
        qbai_perc = cfc_atr["QBAIPerc"].get_value()
        colct = "USSH951A"
        for x in cfcs.keys():
            x.calculate()
            cfc_acc_tbl = x.get_accounts_table()
            agg_cfc_tested_income_amt += cfc_acc_tbl["TestedIncome"].getAmount()*cfcs[x]
            agg_cfc_tested_loss_amt += cfc_acc_tbl["TestedLoss"].getAmount()*cfcs[x]
            net_cfc_tested_income_amt = agg_cfc_tested_income_amt+agg_cfc_tested_loss_amt
            qbai_amt += cfc_acc_tbl["TestedIncomeQBAI"].getAmount()*cfcs[x]
            agg_tested_interest_inc_amt += cfc_acc_tbl["TestedInterestIncome"].getAmount()*cfcs[x]
            agg_tested_interest_exp_amt += cfc_acc_tbl["TestedInterestExpense"].getAmount()*cfcs[x]
            agg_tested_income_tax_amt += cfc_acc_tbl["TestedIncomeTaxes"].getAmount()*cfcs[x]
        

        agg_cfc_tested_income = self._create_account("AggregateCFCTestedIncome",agg_cfc_tested_income_amt)
        agg_cfc_tested_loss = self._create_account("AggregateCFCTestedLoss",agg_cfc_tested_loss_amt)
        net_cfc_tested_income = self._create_account("NetCFCTestedIncome",net_cfc_tested_income_amt)
        qbai = self._create_account("AggregateQBAI",qbai_amt)
        agg_tested_interest_inc = self._create_account("AggregateTestedInterestIncome",agg_tested_interest_inc_amt)
        agg_tested_interest_exp = self._create_account("AggregateTestedInterestExpnese",agg_tested_interest_exp_amt)
        agg_tested_income_tax = self._create_account("AggregateTestedIncomeTax",agg_tested_income_tax_amt)



        specified_interest_exp_amt = max(agg_tested_interest_inc+agg_tested_interest_exp,0)
        dtir = max((qbai*qbai_perc)-specified_interest_exp_amt,0)
        gilti_amt = (-1*net_cfc_tested_income_amt)-dtir
        gilti = self._create_account("GILTI",gilti_amt)
        specified_interest_exp = self._create_account("SpecifiedInterestExpense",specified_interest_exp_amt)

        inclusion_perc = self._create_account("GILTIInclusionPercentage",(gilti_amt/agg_cfc_tested_income_amt))
        sec78grossup = self._create_account("Sec78GrossUpOnGILTI",((gilti_amt/agg_cfc_tested_income_amt)*agg_tested_income_tax_amt))


        agg_cfc_tested_income.account_collection = colct
        agg_cfc_tested_loss.account_collection = colct
        net_cfc_tested_income.account_collection = colct
        qbai.account_collection = colct
        agg_tested_interest_inc.account_collection = colct
        agg_tested_interest_exp.account_collection = colct
        agg_tested_income_tax.account_collection = colct
        inclusion_perc.account_collection = colct
        sec78grossup.account_collection = colct
        gilti.account_collection = colct
        specified_interest_exp.account_collection = colct

        self._accounts_table.add_account(agg_cfc_tested_income)
        self._accounts_table.add_account(agg_cfc_tested_loss)
        self._accounts_table.add_account(qbai)
        self._accounts_table.add_account(net_cfc_tested_income)
        self._accounts_table.add_account(agg_tested_interest_inc)
        self._accounts_table.add_account(agg_tested_interest_exp)
        self._accounts_table.add_account(agg_tested_income_tax)
        self._accounts_table.add_account(inclusion_perc)
        self._accounts_table.add_account(sec78grossup)
        self._accounts_table.add_account(gilti)
        self._accounts_table.add_account(specified_interest_exp)
# p = Period("CYE","2022", "01-01-2022", "12-31-2022")
# tb = TrialBalance(p)
# tb.generate_random_tb()
# e = Entity("Acme Corp","ME","EUR",p,"CFC",tb)

# e.pull_accounts_csv("tests//Misc//accounts.csv")