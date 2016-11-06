import os
import csv

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

rootdir = "C:\\JDeveloper\\mywork\\Application2"

distinct_library_ref = {}
distinct_ext_library_ref = {}
all_jars = []
mapping = {}


def read_mapping(filename):
    mapping = {}
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            mapping[row[0]]= row[1]
        return mapping

def addLibraryReference(etnode, lib):
    hash = ET.SubElement(etnode, "hash")
    id = ET.SubElement(hash, "url")
    id.set("n", "id")
    id.set("path", lib)
    isJDK = ET.SubElement(hash, "value")
    isJDK.set("n", "isJDK")
    isJDK.set("v", "false")


def removeLibraryReferences(etnode, jarnames):
    for hash in etnode:
        id = hash.find("./value[@n='id']")
        if id is not None:
            if id.get('v') in jarnames:
                etnode.remove(hash)

def convert_jpr(filename, outfilename):
    parser = XMLParser(encoding='UTF-8')
    xml = ET.parse(filename, parser)
    xmlDocType = xml.getroot().tag
    ET.register_namespace('jpr', "http://xmlns.oracle.com/ide/project")
    if xmlDocType == "{http://xmlns.oracle.com/ide/project}project":
        to_be_added_library = []
        to_be_removed_library = []
        internalDefinition = xml.getroot().find(".//hash[@n='internalDefinitions']")
        if internalDefinition is not None:
            libraryDefinitions = internalDefinition.find("./list[@n='libraryDefinitions']")
            for libraryDefinition in libraryDefinitions:
                id = libraryDefinition.find("./value[@n='id']")
                lib = mapping[id.get("v")]
                if lib is not None:
                    to_be_added_library.append(lib)
                    libraryDefinitions.remove(libraryDefinition)
                    to_be_removed_library.append(id.get("v"))
        exportedReferences = xml.getroot().find(".//list[@n='exportedReferences']")
        libraryReferences = xml.getroot().find(".//list[@n='libraryReferences']")
        removeLibraryReferences(exportedReferences, to_be_removed_library)
        removeLibraryReferences(libraryReferences, to_be_removed_library)
        for lib in to_be_added_library:
            addLibraryReference(exportedReferences, lib)
            addLibraryReference(libraryReferences, lib)

        #outstring = ET.tostring(xml, encoding='utf8', method='xml')
        #print(xml.tostring())
        xml.write(outfilename, encoding="UTF-8", xml_declaration=True)


mapping = read_mapping("JarToLibrary.txt")
for folder, subs, files in os.walk(rootdir):
    for filename in files:
        if ".jpr" in filename and "classes" not in folder:
            try:
                convert_jpr(os.path.join(folder, filename), os.path.join(folder, "new_" + filename))
            except ET.ParseError as e:
                print("Error, " + os.path.join(folder, filename) + ", " + repr(e))
print(sorted(all_jars))



