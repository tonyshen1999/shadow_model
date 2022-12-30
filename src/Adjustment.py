
class Adjustment:
    def __init__(self,adj_amount, adj_class, adj_collection, adj_period, adj_type,adj_perc = 0, currency = "USD"):
        self.adj_amount = adj_amount
        self.adj_perc = adj_perc
        self.adj_class = adj_class
        self.adj_collection = adj_collection
        self.adj_period = adj_period
        self.adj_type = adj_type
        self.currency = currency
    def apply_adj(self,other):
        if isinstance(other,Adjustment):
            return (self.adj_type,self.adj_class,self.adj_collection,self.adj_period) == (other.adj_type,other.adj_class,other.adj_collection,other.adj_period)
        return False