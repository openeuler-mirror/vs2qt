# vs2qt

#### Description

The VS Engineering Conversion Assistant will provide a sophisticated and convenient way to convert projects from Visual Studio (VS) to cross platform Qt projects.

The successfully converted pro file will be stored in the directory where vcxproj is located, and can be opened through QtCreator. At the same time as the project file conversion is successful, this program will also convert the encoding format of the program file, with the UTF-8 encoding.

#### Environment
1.Linux System
2.Equipped with Python 3.5 to Python 3.11 interpreters

#### User Description

Terminal commands:python3 vs2pro.py root_dir -Lxx -Ixx ...
root_dir	The directory path where the vcxproj file is located

#### Parameters

-I	Header file path for extension
-L	Library file path for extension

