"""Fichier d'installation de notre script salut.py."""


from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = "D:\\Users\\antoine\\AppData\\Local\\Programs\\Python\\Python35\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "D:\\Users\\antoine\\AppData\\Local\\Programs\\Python\\Python35\\tcl\\tk8.6"



def include_OpenGL():
    path_base = "D:\\Users\\antoine\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\OpenGL"
    skip_count = len(path_base) 
    zip_includes = [(path_base, "OpenGL")]
    for root, sub_folders, files in os.walk(path_base):
        for file_in_root in files:
            zip_includes.append(
                    ("{}".format(os.path.join(root, file_in_root)),
                     "{}".format(os.path.join("OpenGL", root[skip_count+1:], file_in_root))
                    ) 
            )      
    return zip_includes

# On appelle la fonction setup
addtional_mods = ['numpy.core._methods', 'numpy.lib.format','OpenGL.arrays.strings']
setup(

    name = "Simu1DDL",

    version = "0.1",

    description = "Ce programme simule la pince",
    options = {'build_exe': {'zip_includes': include_OpenGL(),'includes': addtional_mods}},
    executables = [Executable("main.py")],

)