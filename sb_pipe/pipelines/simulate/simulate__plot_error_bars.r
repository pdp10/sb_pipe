# This file is part of sb_pipe.
#
# sb_pipe is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sb_pipe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with sb_pipe.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
# $Revision: 3.0 $
# $Author: Piero Dalle Pezze $
# $Date: 2016-07-7 16:14:32 $



# Retrieve the environment variable SB_PIPE
SB_PIPE <- Sys.getenv(c("SB_PIPE"))
source(file.path(SB_PIPE, 'sb_pipe','pipelines','simulate','plot_timecourses.r'))


# R Script to plot time courses and collect statistics.
#
# :args[1]: the model name without extension
# :args[2]: the input directory
# :args[3]: the output directory
# :args[4]: the output file name
# :args[5]: the label for the x axis (e.g. Time (min))
main <- function(args) {
    # The model model_noext
    model_noext <- args[1]
    inputdir <- args[2]
    outputdir <- args[3]
    outputfile <- args[4]
    xaxis_label <- args[5]
    
    plot_error_bars_plus_statistics(inputdir, outputdir, model_noext, outputfile, xaxis_label)
}


main(commandArgs(TRUE))
# Clean the environment
rm ( list=ls ( ) )