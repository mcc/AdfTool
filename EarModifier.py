import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

#By Martin, 20161013
import io

excluded_jars = []

def modify_jar(inbuffer):
    outBufferIO = io.BytesIO()
    inBufferIO = io.BytesIO(inbuffer)
    zin = zipfile.ZipFile(inBufferIO, 'r')
    zout = zipfile.ZipFile(outBufferIO, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename[-9:] == 'bc4j.xcfg'):
            try:
                parser = XMLParser(encoding='UTF-8')
                ET.register_namespace('', 'http://xmlns.oracle.com/bc4j/configuration')
                xml = ET.fromstring(buffer, parser)
                ampools = xml.findall('.//{http://xmlns.oracle.com/bc4j/configuration}AM-Pooling')
                isprint = False
                for ampool in ampools:
                    if ampool.get('jbo.dofailover') != None:
                        print('Processing file: ' + item.filename)
                        print('  before: jbo.dofailover=' + ampool.get('jbo.dofailover'))
                        ampool.set('jbo.dofailover', 'false')
                        print('  after: jbo.dofailover=' + ampool.get('jbo.dofailover'))
                        #isprint = True
                outstring = ET.tostring(xml, encoding='utf8', method='xml')
                if isprint:
                    print(outstring)
                zout.writestr(item, outstring)
            except ET.ParseError as e:
                print("Error, " + item.filename+ ", " + repr(e))
            except Exception as e:
                print("Error, " + item.filename + ", " + repr(e))
        else:
            zout.writestr(item, buffer)
    zout.close()
    zin.close()
    return outBufferIO.getvalue()

def modify_war(inbuffer):
    outBufferIO = io.BytesIO()
    inBufferIO = io.BytesIO(inbuffer)
    zin = zipfile.ZipFile(inBufferIO, 'r')
    zout = zipfile.ZipFile(outBufferIO, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename[-4:] == '.jar'):
            zout.writestr(item, modify_jar(buffer))
        else:
            zout.writestr(item, buffer)
    zout.close()
    zin.close()
    return outBufferIO.getvalue()

def modify_ear(infile, outfile):
    zin = zipfile.ZipFile(infile, 'r')
    zout = zipfile.ZipFile(outfile, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename[-4:] == '.war'):
            zout.writestr(item, modify_war(buffer))
        else:
            zout.writestr(item, buffer)
    zout.close()
    zin.close()

if __name__ == '__main__':
    if (len(sys.argv) == 3):
        modify_ear(sys.argv[1], sys.argv[2])
    else:
        print("python " + sys.argv[0] + " <in ear file> <out ear file>")
