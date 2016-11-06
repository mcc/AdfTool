import os
import csv
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

#filename = "D:\\Server_Log\\Prod_DTS2_2016_09_02_154352\\metricdump-20160902.071309.log\\metricdump-20160902.071309.log"


def scannode(csvwriter, prefix, node):
    childs = list(node)
    for child in childs:
        if child.tag == 'noun':
            scannode(csvwriter=csvwriter, prefix=prefix+"."+child.attrib['name'], node=child)
        elif child.tag == 'metric':
            v_obj  = child.find('value')
            value = ""
            u_obj = child.find('unit')
            unit = ""
            d_obj = child.find('description')
            description = ""
            if v_obj != None:
                value = v_obj.text
            if u_obj != None:
                unit = u_obj.text
            if d_obj != None:
                description = d_obj.text
            csvwriter.writerow([prefix+"."+child.attrib['name'], value, unit, description])


def dump2cvs(inputfile, outputfile):
    try:
        parser = XMLParser(encoding='UTF-8')
        xml = ET.parse(inputfile, parser)
        xmlDocType = xml.getroot().tag
        print(xmlDocType)
        with open(outputfile, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',',lineterminator='\n',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for key, attr in xml.getroot().attrib.items():
                csvwriter.writerow([key, attr])
            nouns = xml.getroot().find("statistics").findall("noun")
            for noun in nouns:
                scannode(csvwriter, '', noun)
    except ET.ParseError as e:
        print("Error, " + inputfile + ", " + repr(e))





if __name__ == '__main__':
    if (len(sys.argv) == 3):
        dump2cvs(sys.argv[1], sys.argv[2])
    else:
        print("python " + sys.argv[0] + " <metricdump log file> <output file>")
