from distutils.core import setup
import py2exe
setup(windows=[{"script":"client.py" ,"icon_resources": [(1, "./pic/b.ico")]}],
    options={"py2exe":{"compressed": 1, "bundle_files": 1}}
    )