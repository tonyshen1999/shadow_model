from OrgChart import OrgChart
from Period import Period

class Scenario:
    def __init__(self, periods):
        self.periods = periods
        self.validate_periods()
        self.orgCharts = []
        for x in periods:
            self.orgCharts.append(OrgChart(x))

    def validate_periods(self):
        for x in range(1,len(self.periods)):
            if (self.periods[x-1]+1) != self.periods[x]:
                raise Exception((self.periods[x-1]+1).get_pd() + " should come after "+self.periods[x-1].get_pd())


    def load_org_charts(self):
        pass

periods = [
    Period("CYE",2022),
    Period("CYE",2023),
    Period("CYE",2024)
]

scn = Scenario(periods)

