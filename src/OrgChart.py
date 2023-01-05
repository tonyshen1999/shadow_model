from Entity import Entity, USSH, CFC, DRE

class OrgChart:
    # 
    def __init__(self, period):
        self.period = period
        self.entities = []
    
    def contains(self,entity):
        if entity in self.entities:
            return True
        return False

    def add_entity(self,entity):
        
        if self.contains(entity) == False:
            self.entities.append(entity)

        for x in entity.children.keys():
            if self.contains(x) == False:
                self.entities.append(x)
    def us_calc(self):
        for x in self.entities:
            if isinstance(x,USSH):
                x.calculate()
    def calc_cfcs(self):
        for x in self.entities:
            if isinstance(x,CFC):
                x.calculate()
    def add_to_parent(self,parent,child, percentage):
        parent.children[child] = percentage
    
    def find_entity(self,entity_name):
       
        for x in self.entities:
            if x.name == entity_name:
                return x
        return None

    def get_parents(self):

        parents = []
        for x in self.entities:
            if len(x.parents.keys()) == 0:
                parents.append(x)
        return parents
    #Consolidate

    