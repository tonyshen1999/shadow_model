import pandas as pd

class Period:
    def __init__(self, period_type, period_year, begin_date, end_date):

        self.period_year = period_year
        self.period_type = period_type
        self.begin_date = pd.to_datetime(begin_date)
        self.end_date = pd.to_datetime(end_date)
        # self.prior_period = Period(self.period_type, self.period_year - 1, begin_date - pd.DateOffset(years=1),
        #                            end_date - pd.DateOffset(years=1))
        # self.future_period = Period(self.period_type, self.period_year - 1, begin_date + pd.DateOffset(years=1),
        #                             end_date + pd.DateOffset(years=1))

    def __eq__(self,other):

        return isinstance(other, Period) and (self.period_type, self.period_year) == (other.period_type, other.period_year)

    def __str__(self):
        to_return = self.period_type + str(
            self.period_year) + ", Begin: " + self.begin_date.__str__() + ", End: " + self.end_date.__str__()
        return to_return