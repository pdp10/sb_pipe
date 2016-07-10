#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of sb_pipe.
#
# sb_pipe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sb_pipe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sb_pipe.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
from os.path import isdir, join
import shutil
import glob


def main(args):

  mypath = os.getcwd()
  modelProjects = [f for f in os.listdir(mypath) if isdir(join(mypath, f))]

  for file in modelProjects:
    modelspath = join(file, 'Models')
    paramEstimCopasiFiles = glob.glob(os.path.join(modelspath, "*_param_estim?*.cps"))
    for f in paramEstimCopasiFiles:
      print("deleting..." + f)           
      os.remove(f)
        
    tmppath = join(file, 'tmp')
    # print tmppath
    shutil.rmtree(tmppath, ignore_errors=True)
    
    wfpath = join(file, 'Working_Folder')
    # Delete tgz files
    wflist = [ f for f in os.listdir(wfpath) if f.endswith(".tgz") ]
    for f in wflist:
      print("deleting..." + f)      
      os.remove(os.path.join(wfpath, f))
    # delete sub-directories
    wflist = [d for d in os.listdir(wfpath) if os.path.isdir(os.path.join(wfpath, d))]
    for d in wflist:
      print("deleting..." + d)
      shutil.rmtree(os.path.join(wfpath, d), ignore_errors=True)

main(sys.argv)
