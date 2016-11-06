import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

#By Martin, 20160905

excluded_jars = []


def trans(filename, prefix, elem):
    output = dict()
    _trans(output, filename, prefix, elem)
    return output


def _trans(output, filename, prefix, elem):
    tag = elem.tag.replace("{http://xmlns.oracle.com/bc4j/configuration}", "")
    for attrib in elem.attrib:
        output[prefix + "." + tag + "," + attrib] = elem.attrib[attrib]
    for child in list(elem):
        _trans(output, filename, prefix + "." + tag, child)


def unzip_ear(src, dest, filter):
    with zipfile.ZipFile(src) as zf:
        for zfile in zf.namelist():
            if ".war" in zfile:
                warfile = zipfile.ZipFile(zf.extract(zfile, dest))
                for file_in_war in warfile.namelist():
                    if ".jar" in file_in_war:
                        jar_path = os.path.join(dest,zfile+"_unzip")
                        jarfile = zipfile.ZipFile(warfile.extract(file_in_war, jar_path))
                        for file_in_jar in jarfile.namelist():
                            if filter in file_in_jar:
                                file_path = os.path.join(jar_path , file_in_war+"_unzip")
                                ext_file = jarfile.extract(file_in_jar, file_path)


def analysis_ear(earfile, tempdir):
    rootdir = tempdir
    unzip_ear(earfile, rootdir, ".xml")
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if ".xml" in filename and "classes" not in folder:
                try:
                    parser = XMLParser(encoding='UTF-8')
                    xml = ET.parse(os.path.join(folder, filename), parser)
                    xmlDocType = xml.getroot().tag
                    managed_beans = xml.getroot().findall(".//{http://xmlns.oracle.com/adf/controller}managed-bean")
                    #print(appModules)
                    if managed_beans is not None:
                        for managed_bean in managed_beans:
                            try:
                                scope = ""
                                name = ""
                                clazz = ""
                                for child in list(managed_bean):
                                    if "scope" in child.tag:
                                        scope = child.text
                                    if "name" in child.tag:
                                        name = child.text
                                    if "class" in child.tag:
                                        clazz = child.text
                                print("OK, " + os.path.join(folder, filename) + "," + name + ", " + clazz + "," + scope)
                            except Exception as e:
                                print("Error, " + os.path.join(folder, filename) + ", " + repr(e))
                except ET.ParseError as e:
                    print("Error, " + os.path.join(folder, filename) + ", " + repr(e))
                except Exception as e:
                    print("Error, " + os.path.join(folder, filename) + ", " + repr(e))


earfile1 = "D:\\Martin\\Work\\Source\\for_build\\trunk\\DTSPortal\\deploy\\DTSPortal.ear"
rootdir1 = "D:\\tmp\\DTSPortal3"

#unzip_ear(earfile1, rootdir1)


if __name__ == '__main__':
    if (len(sys.argv) == 3):
        analysis_ear(sys.argv[1], sys.argv[2])
    else:
        print("python " + sys.argv[0] + " <ear file> <temp folder>")
