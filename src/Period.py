import pandas as pd
import  copy as copy
class Period:

    '''
    Period object represents time period in either Calendar Year End or Fiscal Year End
    Attributes:
    1. period_type, either 'FYE' or 'CYE' or 'Blank'
    2. period_year, 2020,2021, etc... can be entered as 'CYE2022' or 2022
    3. begin_date & end_date, entered as string, convert to date time
    '''
    def __init__(self, period_type, period_year, begin_date="", end_date=""):

        if isinstance(period_year,str) and period_type == "":
            if "CYE" not in period_year and "FYE" not in period_year:
                raise Exception(period_year + " is an invalid period format")
            self.period_year = period_year.replace("CYE","").replace("FYE","")
            self.period_type=period_year.replace(self.period_year,"")
            self.period_year = int(self.period_year)

        elif period_type == "CYE" or period_type == "FYE":
            self.period_year = int(period_year)
            self.period_type = period_type
        else:        
            raise Exception(period_type+str(period_year) + " is an invalid period format")

        self.begin_date = pd.to_datetime(begin_date)
        self.end_date = pd.to_datetime(end_date)

    def __eq__(self,other):

        return isinstance(other, Period) and (self.period_type, self.period_year) == (other.period_type, other.period_year)

    def __str__(self):
        to_return = self.period_type + str(
            self.period_year) + ", Begin: " + self.begin_date.__str__() + ", End: " + self.end_date.__str__()
        return to_return
    '''
    Params:  Must be Int. Number of years to add
    Returns: New Period with number of years added
    '''
    def __add__(self, other):
        to_return = copy.deepcopy(self)
        if isinstance(other,int):
            to_return.period_year += other
            to_return.begin_date = to_return.begin_date + pd.DateOffset(years=other)
            to_return.end_date = to_return.end_date + pd.DateOffset(years=other)
        else:
            raise Exception(type(other), other.__str__(), "cannot be added to Period object")
        
        return to_return
    '''
    Params: Must be Int. Number of years to subtract
    Returns: New Period with number of years subtracted
    '''
    def __sub__(self, other):
        to_return = copy.deepcopy(self)
        if isinstance(other,int):
            to_return.period_year = to_return.period_year-other
            to_return.begin_date = to_return.begin_date - pd.DateOffset(years=other)
            to_return.end_date = to_return.end_date - pd.DateOffset(years=other)
        else:
            raise Exception(type(other), other.__str__(), "cannot be subtracted from Period object")
        return to_return

    def get_pd(self):
        return self.period_type + str(self.period_year)
