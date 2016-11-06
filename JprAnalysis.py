import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

rootdir = "C:\\JDeveloper\\mywork\\Application2"

distinct_library_ref = {}
distinct_ext_library_ref = {}

def analysis_jpr(filename):
    parser = XMLParser(encoding='UTF-8')
    xml = ET.parse(filename, parser)
    xmlDocType = xml.getroot().tag
    print(xmlDocType)
    if xmlDocType == "{http://xmlns.oracle.com/ide/project}project":
        #Exported Library (referenced as library
        exportedReferences = xml.getroot().find(".//list[@n='exportedReferences']")
        for hash in exportedReferences:
            if hash.tag == 'hash':
                for value in hash:
                    if value.attrib['n'] == 'id':
                        if value.get('v') is not None:
                            print(value.attrib['v'])
                            distinct_library_ref[value.attrib['v']]=value.attrib['v']
                        elif value.get('path') is not None:
                            print(value.attrib['path'])
                            distinct_ext_library_ref[value.attrib['path']]=value.attrib['path']
        return
        dependencyList = xml.getroot().findall(".//list[@n='dependencyList']")
        for dependency in dependencyList:
            for child in dependency:
                clazz = child.find(".//value[@n='class']")
                url = child.find(".//url[@n='sourceURL']")
                if clazz is not None:
                    print(clazz.get('v') + ', ' + url.get('path'))
                else:
                    print("dependency not in expected format: <" + child.text + ">")
        profileDefinitions = xml.getroot().findall(".//hash[@n='profileDefinitions']")
        for profileDefinition in profileDefinitions:
            profileName = profileDefinition.find(".//value[@n='profileName']")
            profileClass = profileDefinition.find(".//value[@n='profileClass']")
            jarURL = profileDefinition.find(".//url[@n='jarURL']")
            if profileName is not None:
                print(profileName.get('v') + ', ' + profileClass.get('v') + ', ' + jarURL.get('path'))
            else:
                print("Project Definition not in expected format: <" + profileDefinition.text + ">")
        libraryReferences = xml.getroot().findall(".//list[@n='libraryReferences']")
        for libraryReference in libraryReferences:
            hashes = libraryReference.findall(".//hash")
            for hash in hashes:
                id = hash.find("./value[@n='id']")
                if id is not None:
                    print(id.get("v"))
                else:
                    print('exportedReference not in expected format:<' + hash.text + ">")
        internalDefinitions = xml.getroot().findall(".//hash[@n='internalDefinitions']")
        for internalDefinition in internalDefinitions:
            classPath = internalDefinition.find("./list[@n='classPath']")
            if classPath is not None:
                urls = classPath.findall("./url")
                for url in urls:
                    print("url: " + url.get("path"))
                description = internalDefinition.find("./value[@n='description']")
                id = internalDefinition.find("./value[@n='id']")
                print("description: " + description.get("v"))
                print("id: " + id.get("v"))
            else:
                print("internalDefinition not expected: " + internalDefinition.text)





for folder, subs, files in os.walk(rootdir):
    for filename in files:
        if ".jpr" in filename and "classes" not in folder:
            try:
                analysis_jpr(os.path.join(folder, filename))
            except ET.ParseError as e:
                print("Error, " + os.path.join(folder, filename) + ", " + repr(e))



