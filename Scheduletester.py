import copy

import Schedule
import Infogenerator
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring



class ScheduleGenerator:

    def __init__(self, fName, copySchedule):
        self.__fName = fName
        self.__newSchedule = copy.deepcopy(copySchedule)
        self.__gen = Infogenerator.Infogenerator()
        self.__attributes = self.loadAttributes()
        self.loadAttributes()

    def loadAttributes(self):
        address = self.__gen.getRandomAddress()
        print(address)
        generationAttributes = {
            "businessname":self.__gen.getRandomCompanyName(),
            "ein":self.__gen.getRandomEIN(),
            "citynm":address.city,
            "addressline1":address.line1,
            "addressline2":address.line2
        }
        return generationAttributes


    def generateValues(self, generationAttributes = {}):

        if(len(generationAttributes) >= 0):
            self.__attributes = generationAttributes

        values = self.__newSchedule.findTextTags(self.__newSchedule.getRoot())

        for x in values:
            for attrib in self.__attributes:
                if attrib in x.tag.lower():
                    x.text = self.__attributes[attrib]




    def getSchedule(self):
        return self.__newSchedule








sch1 = Schedule.Schedule("files/Page1.xml")
#print(sch1)

generationAttributes = {
    "businessname": "poopy butthole",
    "ein":"333333333",
    "city": "miami"
}

scheduleGenerator = ScheduleGenerator("hi",sch1)
scheduleGenerator.generateValues(generationAttributes)
scheduleGenerator.loadAttributes()


