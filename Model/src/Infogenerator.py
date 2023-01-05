import random

class Address:
    def __init__(self, list):
        self.list = list
        self.line1 = list[0]
        self.line2 = list[1]
        self.zip = list[2]
        self.city = list[3]
        self.state = list[4]
        self.country = list[5]

    def __str__(self):
        return self.line1 + ", " + self.line2 + ", " + self.zip + ", " + self.city + ", " + self.state + ", " + self.country



class Infogenerator:
    def __init__(self, addressFile = "", nameFile = ""):
        self.__addressFile = ""
        self.__nameFile = ""
        self.__addressSet = []
        self.__addressSet = set(self.__addressSet)
        self.__nameSet = []
        self.__nameSet = set(self.__nameSet)
        self.loadAddress()
        self.loadNames()

    def loadAddress(self, fName = "/Users/tonyshen/PycharmProjects/TRA/files/Testing/AddressNames.txt"):
        fileRead = open(fName, "r")

        for line in fileRead:
            address = line.split(",")
            self.__addressSet.add(Address(address))

    def loadNames(self, fName = "/Users/tonyshen/PycharmProjects/TRA/files/Testing/CompanyNames.txt"):
        fileRead = open(fName, "r")

        for line in fileRead:
            self.__nameSet.add(line.strip("\n"))


    def getRandomAddress(self):
        return self.__addressSet.pop()

    def getRandomCompanyName(self):
        return self.__nameSet.pop()

    def getRandomEIN(self):

        num = 0
        for i in range(0,9):
            num = num*10 + random.randint(0,9)

        return str(num)


