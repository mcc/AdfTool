import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

rootdir = "C:\\JDeveloper\\mywork\\Application2"

distinct_library_ref = {}
distinct_ext_library_ref = {}
all_jars = []

def analysis_jpr(filename):
    parser = XMLParser(encoding='UTF-8')
    xml = ET.parse(filename, parser)
    xmlDocType = xml.getroot().tag
    if xmlDocType == "{http://xmlns.oracle.com/ide/project}project":
        internalDefinitions = xml.getroot().findall(".//hash[@n='internalDefinitions']")
        for internalDefinition in internalDefinitions:
            classPath = internalDefinition.find(".//list[@n='classPath']")
            description = internalDefinition.find("./value[@n='description']")
            id = internalDefinition.find(".//value[@n='id']")
            if classPath is not None:
                urls = classPath.findall("./url")
                for url in urls:
                    #print("url: " + url.get("path"))
                    print(id.get("v") + "," + url.get("path") + "," + filename)
                    all_jars.append([id.get("v"),url.get("path"), filename])
            else:
                print("internalDefinition not expected: " + internalDefinition.text)

for folder, subs, files in os.walk(rootdir):
    for filename in files:
        if ".jpr" in filename and "classes" not in folder:
            try:
                analysis_jpr(os.path.join(folder, filename))
            except ET.ParseError as e:
                print("Error, " + os.path.join(folder, filename) + ", " + repr(e))

print(sorted(all_jars))



