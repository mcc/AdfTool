import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

rootdir = "D:\\Martin\\Work\\Source\\trunk"


for folder, subs, files in os.walk(rootdir):
    for filename in files:
        if ".xml" in filename and "classes" not in folder:
            try:
                parser = XMLParser(encoding='UTF-8')
                xml = ET.parse(os.path.join(folder, filename), parser)
                xmlDocType = xml.getroot().tag

                #print(xml.getroot().findall(".//AttrArray[@Name='KeyAttributes']"))
                if xmlDocType == "{http://xmlns.oracle.com/bc4j}ViewObject":
                    passivateMode = "Passivate"
                    if "Passivate" in xml.getroot().attrib:
                        passivateMode=xml.getroot().attrib['Passivate']
                    keyAttr = xml.getroot().findall("./{http://xmlns.oracle.com/bc4j}AttrArray[@Name='KeyAttributes']")
                    if len(keyAttr) == 0:
                        print(passivateMode + ", " + os.path.join(folder, filename) + " has no KeyAttr")
                #print(xml.getroot().findall("./{http://xmlns.oracle.com/bc4j}Properties"))
            except ET.ParseError as e:
                print("Error, " + os.path.join(folder, filename) + ", " + repr(e))



