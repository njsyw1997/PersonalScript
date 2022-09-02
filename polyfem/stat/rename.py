import glob
import json
import math
import os
import subprocess
import tempfile
from unittest import result
import numpy as np
from sqlalchemy import true
import signal

from sympy import false

path_list=glob.glob("/home/yiwei/results/**/**/**/**/**")
for path in path_list:
    dirname=os.path.dirname(path)
    basename=os.path.basename(path)
    if(basename=="P3"):
        os.rename(path,dirname+"/P2")

        