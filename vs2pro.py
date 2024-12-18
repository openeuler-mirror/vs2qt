#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: linzhuo
@data: 2023/08/10
@describe: 将VS项目工程文件转换为Qt使用的Pro项目文件
"""

import os
import sys
import re
import glob
import xml.dom.minidom
import chardet
import codecs

class VS2make():

    def __init__(self):
        self.name = ""
        self.version = "0.0.0"
        

    def __str__(self):
        msg = ("valid: " if self.isValid else "invalid: ") + self.name + "\t" + self.version + "\t"
        if self.absolute_path :
            return msg + self.absolute_path
        elif self.rel_path :
            return msg + self.rel_path
        else :
            return msg

    #查找vs工程文件.vcxproj
    def search_vcxproj(self, VS_path):
       filesvs = os.listdir(VS_path)
       if not os.path.isdir(VS_path):
           print("传入的参数不是目录")
           return False
       print("要搜索的目录： " + VS_path)
       vspath_name = glob.glob(os.path.join(VS_path, "*.vcxproj"))

       if not len(vspath_name):
           print("在" + VS_path + " 没有搜索到.vcxproj 文件")
           return False
       return vspath_name

    #搜索cpp .h .c .hpp文件 
    def find_files_specified_suffix(self, target_dir, target_suffix="cpp"):
        find_res = []
        target_suffix_dot = "." + target_suffix
        walk_generator = os.walk(target_dir)
        for root_path, dirs, files in walk_generator:
         if len(files) < 1:
            continue
         for file in files:
            file_name, suffix_name = os.path.splitext(file)
            if suffix_name == target_suffix_dot:
                find_res.append(os.path.join(root_path, file))
        return find_res

    #find_files_specified_suffix("./", "txt")
    #解析vcxproj_path
    def analysis_VCXPROJ(self, vcxproj_path):
        print("开始解析 "  + vcxproj_path)
        # 使用minidom解析器打开 XML 文档
        find_listlib = []
        find_listqtmoudles = []
        DOMTree =  xml.dom.minidom.parse(vcxproj_path)
        collection = DOMTree.documentElement

        #QtModules 标签
        property_groups = collection.getElementsByTagName("PropertyGroup")
        for property_group in property_groups:
            qt_modules = property_group.getElementsByTagName("QtModules")
            #if not qt_modules  is None:
            for  qt_module in qt_modules:
                qt_modulelist = str(qt_module.firstChild.data).split(';')
                find_listqtmoudles +=  qt_modulelist

        #删除重复值
        list(set(find_listqtmoudles))   
        #链接库标签
        link_libs = collection.getElementsByTagName("ItemDefinitionGroup")
        #头文件和源文件 标签
        item_groups = collection.getElementsByTagName("ItemGroup")

        for link_lib in link_libs:
            #寻找链接库
            links =  link_lib.getElementsByTagName("Link")
            for link in links:
                lib_names = link.getElementsByTagName("AdditionalDependencies")
                for lib_name in lib_names:        
                    list_libs = str(lib_name.firstChild.data).split(';')
                    del(list_libs[-1])
                    #print("使用的链接库" +lib_name.firstChild.data)
                    #print("使用的链接库" + list_libs)
                    #引用的动态库，有可能有重复的内容，进行去除
                    find_listlib = find_listlib + list_libs

        #删除重复值
        list(set(find_listlib))
        
        include_listnames = []
        qtmoc_listnames = []
        clcompile_listnames =[]
        qtuic_listnames = []
        qtrcc_listnames = []
        for item_group in  item_groups:
           #寻找头文件
            include_names = item_group.getElementsByTagName("ClInclude")
            for include_name in  include_names:
               include_listname  = include_name.getAttribute("Include")
               include_listnames.append(str(include_listname))
               qtmoc_names = item_group.getElementsByTagName("QtMoc")
               if not qtmoc_names is None: 
                   for qtmoc_name in  qtmoc_names:
                       qtmoc_listname =  qtmoc_name.getAttribute("Include")
                       include_listnames.append(str(qtmoc_listname)) 
            custom_build_id_includes = item_group.getElementsByTagName("CustomBuild")
            for custom_build_id_include in  custom_build_id_includes:
                custom_build_id_inlist  = custom_build_id_include.getAttribute("Include")
                if "qrc" in custom_build_id_inlist:
                    qtrcc_listnames.append(custom_build_id_inlist)
                    continue
                #if "\\" in (str(include_listname)):
                #custom_build_id_inlist.replace('\\','/')
                include_listnames.append(custom_build_id_inlist)

            #寻找源文件 .c .cpp
            clcompiles = item_group.getElementsByTagName("ClCompile")
            for clcompile  in clcompiles:
                clcompile_listname  = clcompile.getAttribute("Include")
                clcompile_listnames.append(clcompile_listname)
       
            #qtUic判断
            qtuic_names =  item_group.getElementsByTagName("QtUic")
            #vcxproj 是否存在QtUic节点
            if not qtuic_names is None:
                for qtmoc_name in qtuic_names:
                   qtuic_namelist = qtmoc_name.getAttribute("Include")
                   qtuic_listnames.append(str(qtuic_namelist))

            #QtRcc 判断
            qtrcc_names =  item_group.getElementsByTagName("QtRcc")
            #vcxproj 是否存在Qtrcc节点
            if not qtrcc_names is None:
                for qtrcc_name in qtrcc_names:
                   qtrcc_namelist = qtrcc_name.getAttribute("Include")
                   qtrcc_listnames.append(str(qtrcc_namelist))   

        list(set(clcompile_listnames))
        list(set(include_listnames))
        list(set(qtuic_listnames))
        list(set(qtrcc_listnames))
        find_listqtmoudless = list(set(find_listqtmoudles)) 

        print("解析的链接库： ",find_listlib,"\n")
        print("解析的头文件： ",include_listnames,"\n")
        print("解析的源文件： ",clcompile_listnames,"\n")
        print("解析的QTUIC： ",qtuic_listnames,"\n")
        print("解析的QTRcc： ",qtrcc_listnames,"\n")
        print("解析的QTmoudle: ",find_listqtmoudless,"\n")

        return include_listnames, clcompile_listnames, find_listlib, qtuic_listnames, qtrcc_listnames, find_listqtmoudless
    
    #生成pro 文件
    def create_pro (self, find_vsname, include_listnames, find_listlib, clcompile_listnames, qtuic_listnames, qtrcc_listnames, find_listqtmoudless, INCLUDEPATH, LIBS):
        #判断文件是否存在

        if find_vsname.endswith(".vcxproj"):
          #  find_vsname[8:-1]=".pro"
            pro_name = find_vsname[:-7]+"pro"
            print("创建pro文件 ：",pro_name)

        if  os.path.exists(pro_name):
            os.remove(pro_name)
        fpro = open(pro_name,'w+')
        fpro.write("#本文件北京麟卓VS转换工具生成\n")
        fpro.write("TEMPLATE = app\n")
        fpro.write("LANGUAGE = C++\n")
        fpro.write("CONFIG += warn_on release\n")
        fpro.write("OBJECT_DIR += obj\n")
        fpro.write("TARGET += $(OutDir)\\$(ProjectName)\n")
        fpro.write("UI_DIR += QT_GENERATION/UI\n")
        fpro.write("RCC_DIR += QT_GENERATION/RCC\n")
        fpro.write("RCC_DIR +=QT_GENERATION/RCC\n")
        fpro.write("OBJECT_DIR += obj\n")
        fpro.write("INCLUDEPATH += "+INCLUDEPATH + "\n")
        fpro.write("HEADERS += ")
        for includelist in include_listnames:
            includelist = includelist.replace('\\','/')         
            fpro.write("\\\n\t\t"+includelist)

        fpro.write("\nLIBS += " + LIBS) 
        fpro.write("\nLIBS += ")
        for listlib in find_listlib:
            #对osg库单独处理 
            if listlib == "osgd.lib":
                listlib = "osg.lib"
            elif listlib == "osgDBd.lib":
                listlib = "osgDB.lib"
            elif listlib == "osgParticled.lib":
                listlib = "osgParticle.lib"
            elif listlib == "osgQtd.lib":
                listlib = "osgQt.lib"
            elif listlib == "osgGAd.lib":
                listlib = "osgGA.lib"
            elif listlib == "osgUtild.lib":
                listlib = "osgUtil.lib"
            elif listlib == "osgViewerd.lib":
                listlib = "osgViewer.lib"
            elif listlib == "osgManipulatord.lib":
                listlib = "osgManipulator.lib"
            elif listlib == "osgOpenThreadsd.lib":
                listlib = "osgOpenThreads.lib"
            elif listlib == "osgAnimationd.lib":
                listlib = "osgAnimation.lib"
            elif listlib == "osgFXd.lib":
                listlib = "osgFX.lib"
            elif listlib == "osgPresentationd.lib":
                listlib = "osgPresentation.lib"
            elif listlib == "osgSimd.lib":
                listlib = "osgSim.lib"    
            elif listlib == "osgTerraind.lib":
                listlib = "osgTerrain.lib"
            elif listlib == "osgTextd.lib":
                listlib = "osgText.lib"
            elif listlib == "osgUId.lib":
                listlib = "osgUI.lib"
            elif listlib == "osgVolumed.lib":
                listlib = "osgVolume.lib"
            elif listlib == "osgWidgetd.lib":
                listlib = "osgWidget.lib"
            
            listlib = "-l" + listlib[:-4]
            #fpro.write("\t\t"+listlib+ " \\"+"\n")
            fpro.write("\\\n\t\t" + listlib)
        
        fpro.write("\nQT += core gui")
        for find_listqtmoudles in find_listqtmoudless:
            fpro.write("\\\n\t\t" + find_listqtmoudles)
        fpro.write("\nSOURCES +=  ")
        for clcompile_listname in clcompile_listnames:
            fpro.write("\\\n\t\t" + clcompile_listname.replace('\\','/')  )
        fpro.write("\nFORMS += ")
        for qtuic_listname in qtuic_listnames:
            fpro.write("\\\n\t\t" + qtuic_listname)
        fpro.write("\nRESOURCES +=  ")
        for qtrcc_listname in qtrcc_listnames:
            fpro.write("\\\n\t\t" + qtrcc_listname)

    def write_pro_INCLUDEPATH(self, fpro, lib_include):
        fpro.write(lib_include)
        
    # 获取文件编码类型
    def get_encoding(self, file):
    # 二进制方式读取，获取字节数据，检测类型
        with open(file, 'rb') as f:
            data = f.read()
            return chardet.detect(data)['encoding']

    # 读取文件夹下文件 的c文件 cpp 文件 .h 文件 .java 文件 .py文件 .xml 文件 .html .js .qss .qrc
    #.vcxproj  
    #可以指定格式转换
    def get_listpath(self, dir, fileformat, list_full_name):
        names = os.listdir(dir)#获取当前目录下所有文件名及目录名
        formatset = (".c", ".cpp", ".h", ".py", ".xml", ".js", ".qss", ".qrc", ".vcxproj", ".java", ".hpp", ".pro", ".fortran", ".f", ".for", ".f90", ".f95", ".F", ".F90", ".F95", "txt", ".json")
        
        for name in names:
            full_name = dir + '/' + name # 拼接成完整路径
            if os.path.isdir(full_name):
                #list_full_name.append(full_name)
            # print(full_name)
                self.get_listpath(full_name, fileformat, list_full_name)#递归遍历子目录下文件及目录
            else:
                #分离 文件名和扩展名
                filename, extension_name = os.path.splitext(full_name)
                if fileformat == "all" :
                    if not extension_name in formatset :
                        continue
                    else:
                        list_full_name.append(full_name)
                elif fileformat in formatset :
                    if extension_name ==  fileformat:
                        #print(full_name)
                        list_full_name.append(full_name)
        return list_full_name

# 编码转换 utf-8 文件名 编码从什么转换成什么
    def change_coding(self, filename_in, encode_in, encode_out):    
        filename_out = str(filename_in)+"-"+encode_out
        print("filename_out " + filename_out )
        with codecs.open(filename_in, mode='r', encoding=encode_in) as fi:
            data = fi.readlines()
            fi.close()

        with open(filename_out, mode='w', encoding=encode_out) as fo:
            for line in data:                
                fo.write(line)
            fo.close()

       # os.remove(filename_in)
      #  os.rename(filename_out,filename_in)
        with codecs.open(filename_out, mode='rb') as f:
           data = f.read()      
           f.close()
           print(filename_out + " 由 " + encode_in+" 转换后的文件" + chardet.detect(data)['encoding'])

    def change_filecoding(self, file, in_enc, out_enc):
        in_enc = in_enc.upper()
        out_enc = out_enc.upper()
        try:
            print("convert [ " + file.split('\\')[-1] + " ].....From " + in_enc + " --> " + out_enc )
            f = codecs.open(file, 'r', in_enc)
            new_content = f.read()
            codecs.open(file, 'w', out_enc).write(new_content)
        # print (f.read())
        except IOError as err:
            print("I/O error: {0}".format(err))

# 批量编码转换
    def  all_change_coding(self, listpath):
        for utf8file in listpath: 
            #print("utf8file " + utf8file)        
            codename = self.get_encoding(utf8file)
            print(utf8file + " 文件格式 ："+ codename)
            if codename  == "None" or codename == "ASCII" or codename == "ascii"  :
                continue
          #  print("扫描到的文件" +utf8file+" " +str(codename))
            if not str(codename) == "utf-8":
                #self.change_coding(utf8file,codename,"utf-8")
                self.change_filecoding(utf8file, codename, "utf-8")

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("       python3   .py root_dir -Lxx -lxx -Ixx ......  ")
        sys.exit(-1)

    # -I -L 用户用于扩展的头文件路径和库文件路径
    INCLUDEPATH=""
    LIBS=""
    argvnum = len(sys.argv) 
    if argvnum > 2:
        if ((sys.argv)[1])[0:2] == "-c":
            #执行编码转换
            # 编码转化
            vs2make = VS2make()
            search_path = sys.argv[2]
            print("支持转换的格式" + ".c" + ".cpp" + ".h" + ".py" + ".xml" + ".js" + ".qss" + ".qrc" + ".vcxproj" + ".java" + ".hpp" + ".pro" + ".fortran" + ".f" + ".for" + ".f90" + ".f95" + ".F" + ".F90" + ".F95" + ".txt" + ".json")
            list_full_name = []
            listpath = vs2make.get_listpath(search_path, "all", list_full_name)
            vs2make.all_change_coding(listpath)
            sys.exit(0)

        #执行转换
        for i in range(2, argvnum):
            #print((sys.argv)[i])
            tmp = ((sys.argv)[i])[0:2]          
            if tmp == "-I":
                INCLUDEPATH+="\\\n\t\t"+(sys.argv)[i]
            elif tmp == "-L":
                LIBS += "\\\n\t\t"+(sys.argv)[i]
            elif tmp == "-l":
                LIBS += "\\\n\t\t"+(sys.argv)[i]
            else :
                continue
    
    search_path = sys.argv[1]
    vs2make = VS2make()
    find_vsname = vs2make.search_vcxproj(search_path)
    print(find_vsname[0])
    #vs2make.analysis_VCXPROJ(find_vsname[0])
    include_listnames, clcompile_listnames, find_listlib, qtuic_listnames, qtrcc_listnames, find_listqtmoudless = vs2make.analysis_VCXPROJ(find_vsname[0])
    vs2make.create_pro(find_vsname[0], include_listnames, find_listlib, clcompile_listnames, qtuic_listnames, qtrcc_listnames, find_listqtmoudless, INCLUDEPATH, LIBS)

    # 编码转化
    print("支持转换的格式" + ".c" + ".cpp" + ".h" + ".py" + ".xml" + ".js" + ".qss" + ".qrc" + ".vcxproj" + ".java" + ".hpp" + ".pro" + ".fortran" + ".f" + ".for" + ".f90" + ".f95" + ".F" + ".F90" + ".F95" + ".txt" + ".json")
    list_full_name = []
    listpath = vs2make.get_listpath(search_path, "all", list_full_name)
    vs2make.all_change_coding(listpath)

