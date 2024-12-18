# vs2qt

#### 介绍
VS工程转换助手将提供一种精巧便捷的方式，将原本Visual Studio（VS）的工程转换为跨平台的Qt工程。

转换成功的pro文件将会存放至vcxproj所在目录，通过QtCreator打开即可。项目文件转换成功的同时，本程序也会将程序文件的编码格式进行转换,目标编码utf-8。
#### 运行环境

1.  Linux系统
2.  具备python3.5～python3.9解释器

#### 使用说明

命令行方式运行：python3 vs2pro.py root_dir -Lxx -Ixx ...
```sh
root_dir	vcxproj文件所在目录路径 
```
可选参数：
```sh
-I	用于扩展的头文件路径
-L	用于扩展的库文件路径
```


