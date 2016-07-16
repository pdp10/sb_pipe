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
#
#
# Object: Execute the model several times for deterministic or stochastical analysis
#
#
# $Revision: 3.0 $
# $Author: Piero Dalle Pezze $
# $Date: 2016-06-23 13:45:32 $




import os
import sys
import glob
from subprocess import Popen,PIPE

SB_PIPE = os.environ["SB_PIPE"]
sys.path.append(os.path.join(SB_PIPE,'sb_pipe','utils','python'))
from ParamEstim_CollectResults import retrieve_final_estimates
from ParamEstim_CollectResults import retrieve_all_estimates

import sb_param_estim__copasi_utils_plot_calibration





# Input parameters
# input_dir, results_dir, fileout_final_estims, fileout_all_estims, plots_dir, best_fits_percent, data_point_num
def main(input_dir, results_dir, fileout_final_estims, fileout_all_estims, plots_dir, best_fits_percent, data_point_num):

  if not os.path.exists(input_dir) or not os.listdir(input_dir): 
    print("ERROR: input_dir " + input_dir + " does not exist or is empty. Generate some data first.");
    return
  
  if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)
  
  print("Collect results:")
  # Collect and summarises the parameter estimation results
  retrieve_final_estimates(input_dir, results_dir, fileout_final_estims)
  retrieve_all_estimates(input_dir, results_dir, fileout_all_estims)  

  # plot the fitting curve using data from the fit sequence 
  # This requires extraction of a couple of fields from the Copasi output file for parameter estimation.
  #sb_param_estim__copasi_utils_plot_calibration.main(results_dir, results_dir)


  print("\n")
  print("Plot distributions:")
  print("\n")
  process = Popen(['Rscript',
		   os.path.join(SB_PIPE,'sb_pipe','pipelines', 'sb_param_estim__copasi', 'main_final_fits_analysis.r'),
		   os.path.join(results_dir, fileout_final_estims),
		   plots_dir,
		   str(best_fits_percent)])
  process.wait()  
  process = Popen(['Rscript', os.path.join(SB_PIPE,'sb_pipe','pipelines', 'sb_param_estim__copasi', 'main_all_fits_analysis.r'), 
		   os.path.join(results_dir, fileout_all_estims), plots_dir, str(data_point_num)])
  process.wait()  
  