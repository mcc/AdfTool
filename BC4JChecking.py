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


def unzip_ear(src, dest):
    with zipfile.ZipFile(src) as zf:
        for zfile in zf.namelist():
            if ".war" in zfile:
                warfile = zipfile.ZipFile(zf.extract(zfile, dest))
                for file_in_war in warfile.namelist():
                    if ".jar" in file_in_war:
                        jar_path = os.path.join(dest,zfile+"_unzip")
                        jarfile = zipfile.ZipFile(warfile.extract(file_in_war, jar_path))
                        for file_in_jar in jarfile.namelist():
                            if "bc4j.xcfg" in file_in_jar:
                                bc4j_path = os.path.join(jar_path , file_in_war+"_unzip")
                                bc4j = jarfile.extract(file_in_jar, bc4j_path)

def analysis_ear(earfile, tempdir):
    rootdir = tempdir
    unzip_ear(earfile, rootdir )
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if "bc4j.xcfg" in filename and "classes" not in folder:
                try:
                    parser = XMLParser(encoding='UTF-8')
                    xml = ET.parse(os.path.join(folder, filename), parser)
                    xmlDocType = xml.getroot().tag
                    appModules = xml.getroot().findall("./{http://xmlns.oracle.com/bc4j/configuration}AppModuleConfigBag")
                    #print(appModules)

                    for appModule in appModules:
                        try:
                            value_dict = trans(os.path.join(folder, filename), appModule.attrib['ApplicationName'] + ", ", appModule)
                            #if value_dict.get(appModule.attrib['ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.AM-Pooling,jbo.dofailover") is None:
                            #    print(appModule.attrib['ApplicationName']+".AppModuleConfigBag.AppModuleConfig.AM-Pooling,jbo.dofailover is missing");
                            if value_dict.get(appModule.attrib['ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Database,jbo.server.internal_connection") is None:
                                db_conn = value_dict.get(appModule.attrib[
                                                             'ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Custom,JDBCDataSource")
                                if db_conn == None:
                                    db_conn = ""
                                internal_conn = value_dict.get(appModule.attrib[
                                                                   'ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Database,jbo.server.internal_connection")
                                if internal_conn == None:
                                    internal_conn = "None";
                                print(os.path.join(folder, filename) + "," + appModule.attrib['ApplicationName']+".AppModuleConfigBag.AppModuleConfig.AM-Pooling,jbo.server.internal_connection is missing" + "," +
                                      internal_conn + "," + db_conn
                                      );
                            elif value_dict.get(appModule.attrib['ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Database,jbo.server.internal_connection") != 'jdbc/cigDS':
                                db_conn = value_dict.get(appModule.attrib['ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Custom,JDBCDataSource")
                                if db_conn == None:
                                    db_conn = ""
                                internal_conn = value_dict.get(appModule.attrib['ApplicationName'] + ", .AppModuleConfigBag.AppModuleConfig.Database,jbo.server.internal_connection")
                                if internal_conn == None:
                                    internal_conn = "None";
                                print(os.path.join(folder, filename) + "," + appModule.attrib['ApplicationName']+".AppModuleConfigBag.AppModuleConfig.Database,jbo.server.internal_connection is incorrect, actual=" +
                                          internal_conn + "," + db_conn
                                      );
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
