import pandas as pd

class AttributesTable:
    def __init__(self, fName):
        atr_df = pd.read_csv("Attributes//"+fName)
        self.attributes = []
        self.attributes = set(self.attributes)

        for index, row in atr_df.iterrows():
            atr = Attribute(atr_name=row["AttributeName"],atr_value=row["AttributeValue"],atr_begin=row["AttributeStartDate"],atr_end=row["AttributeEndDate"])
            self.attributes.add(atr)

    def __str__(self):
        to_return = ""
        for x in self.attributes:
            to_return += x.__str__() + "\n"
        return to_return
    
class Attribute:
    def __init__(self, atr_name,atr_value,atr_begin,atr_end=""):
        self.atr_name = atr_name
        if isinstance(atr_value, str):
            if atr_value == "Yes":
                atr_value = True
            elif atr_value == "No":
                atr_value = False
        self.atr_value = atr_value
        self.atr_beg = atr_begin
        self.atr_end = atr_end
    def __str__(self):
        to_return = self.atr_name + ": " + str(self.atr_value) + ", begin: " + str(self.atr_beg) + ", end:" + str(self.atr_end)

        return to_return

atr = AttributesTable("CFCAttributes.csv")
print(atr)