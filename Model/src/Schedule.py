import xml.etree.ElementTree as ET
from enum import Enum
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import copy

class Method(Enum):
    TAG = 0
    TEXT = 1
    ATTRIB = 2


class Schedule:

    def __init__(self, fPath, root=Element("DEFAULT")):

        self.fName = fPath
        if root.tag=="DEFAULT":
            tree = ET.parse(fPath)
            self.__root = tree.getroot()
        else:
            self.__root = root

        self.__formName = self.__root.tag




    def getRoot(self):
        return self.__root

    def findTag(self, root, tofind):

        if tofind == root.tag:
            return root
        else:
            for x in root:
                result = self.findTag(x, tofind)
                if result is not None:
                    return result
        return None

    # Function: returns list of nodes that contain values (rather than headers)
    # Parameter: root node
    # Returns: List containing nodes with form values
    def findTextTags(self, root):
        textTags = []
        self.findTextTagsHelper(root,textTags)
        return textTags

    def findTextTagsHelper(self, root, textTags):

        rootText = root.text
        if len(rootText.strip()) > 0:
            #print(root.tag + " text: " + root.text.strip())
            textTags.append(root)
        for x in root:
            self.findTextTagsHelper(x, textTags)

    # Function: Finds tags based on search criteria
    # Parameter: root node, text to find, method = 0 (Default) searches by tags, method = 1 searches by text, method = any other valu search attrib
    # Returns: List containing nodes with form values
    def findNodes(self, root, tofind, method=Method.TAG, approximate=False):
        foundroots = []
        self.findNodesHelper(root,tofind,foundroots, method, approximate)
        return foundroots

    def __tostringhelper(self,root,toReturn, level):

        if root is not None and root.text is not None:
            rootText = root.text.strip()

            if len(rootText)>0:
                rootText = ": " + rootText

            line = (level * "\t") + "<" +root.tag + ">" + rootText+ "\n"

            toReturn.append(line)
            for x in root:
                self.__tostringhelper(x,toReturn, level+1)

            line = (level * "\t")+ "</" +root.tag + ">\n"
            toReturn.append(line)

    def __str__(self):

        toReturn = [self.__formName + "\n"]
        self.__tostringhelper(self.__root,toReturn,0)
        text = "";
        for line in toReturn:
            text += line
        return text


    def findNodesHelper(self, root, tofind, foundroots, method, approximate):

        search = ""
        contains = False

        if method == Method.TAG:
            search = root.tag
        elif method == Method.TEXT:
            search = root.text
        else:
            search = root.attrib

        if approximate and tofind.lower() in search.lower():
            contains = True

        if tofind == search or contains:
            foundroots.append(root)
            return
        else:
            for x in root:
                self.findNodesHelper(x,tofind,foundroots, method, approximate)

#
# sch1 = Schedule("files/Page1.xml")
# root = sch1.getRoot()
# irs5471 = sch1.findNodes(root, "5471",Method.TAG,True)
#
# for x in irs5471:
#     print(x.tag)


