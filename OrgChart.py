from Entity import Entity

class OrgChart:
    # 
    def __init__(self, parent_name, parent_country, period, parent_type, parent_tb):
        self.period = period
        self.parent = Entity(parent_name,parent_country,period, parent_type, parent_tb)

    #Consolidate

    