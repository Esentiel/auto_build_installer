from distutils.core import setup
import py2exe
 
setup(
    windows=[{"script":"client.py"}],
    options={"py2exe": {"includes":["twisted", "PIL", "paramiko", "zope.interface"]}}
)