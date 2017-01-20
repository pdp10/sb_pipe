#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of sbpipe.
#
# sbpipe is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sbpipe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with sbpipe.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Object: Execute the model several times for deterministic or stochastic analysis
#
#
# $Revision: 3.0 $
# $Author: Piero Dalle Pezze $
# $Date: 2016-06-23 13:45:32 $

import logging
import os
import multiprocessing
import subprocess
import shlex
logger = logging.getLogger('sbpipe')


def parcomp(cmd, cmd_iter_substr, cluster_type, runs, output_dir, pp_cpus=1):
    """
    Generic funcion to run a command in parallel

    :param cmd: the command string to run in parallel
    :param cmd_iter_substr: the substring of the iteration number. This will be replaced in a number automatically
    :param cluster_type: the cluster type among pp (Python multiprocessing), sge, or lsf
    :param runs: the number of runs
    :param output_dir: the output directory
    :param pp_cpus: the number of cpus that pp should use at most
    """
    logger.debug("Parallel computation using " + cluster_type)
    logger.debug("Command: " + cmd)
    logger.debug("Iter ID string: " + cmd_iter_substr)
    logger.debug("# runs: " + str(runs))
    if cluster_type == "sge" or cluster_type == "lsf":
        out_dir = os.path.join(output_dir, 'out')
        err_dir = os.path.join(output_dir, 'err')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if not os.path.exists(err_dir):
            os.makedirs(err_dir)

        if cluster_type == "sge":  # use SGE (Sun Grid Engine)
            run_jobs_sge(cmd, cmd_iter_substr, out_dir, err_dir, runs)

        elif cluster_type == "lsf":  # use LSF (Platform Load Sharing Facility)
            run_jobs_lsf(cmd, cmd_iter_substr, out_dir, err_dir, runs)

    else:  # use pp by default (parallel python). This is configured to work locally using multi-core.
        if cluster_type != "pp":
            logger.warn(
                "Variable cluster_type is not set correctly in the configuration file. "
                "Values are: pp, lsf, sge. Running pp by default")
        run_jobs_pp(cmd, cmd_iter_substr, runs, pp_cpus)


def call_proc(params):
    """
    Run a command using Python subprocess.

    :param params: A tuple containing (the string of the command to run, the command id)
    """
    cmd, id = params
    logger.info('Starting Task ' + id)
    # p = subprocess.call(shlex.split(cmd))  # Block until cmd finishes
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out, err


def run_jobs_pp(cmd, cmd_iter_substr, runs, pp_cpus=1):
    """
    Run jobs using python multiprocessing locally.

    :param cmd: the full command to run as a job
    :param cmd_iter_substr: the substring in command to be replaced with a number
    :param runs: the number of runs to execute
    :param pp_cpus: The number of available cpus. If pp_cpus <=0, all the available cores will be used.
    """

    # Create a Pool.
    pool = multiprocessing.Pool(1)
    if pp_cpus > 0:
        # Create a pool with pp_cpus
        pool = multiprocessing.Pool(pp_cpus)

    logger.info("Starting parallel computation:")

    results = []
    for i in xrange(1, runs + 1):
        params = (cmd.replace(cmd_iter_substr, str(i)), str(i))
        results.append(pool.apply_async(call_proc, (params,)))

    # Close the pool and wait for each running task to complete
    pool.close()
    pool.join()

    # Print the status of the parallel computation.
    if len(results) != runs:
        logger.error("Some computation failed. Do all output files exist?")
    else:
        logger.info("Parallel computation terminated.")
        logger.info("If errors occur, check that " + cmd.split(" ")[0] + " runs correctly.")

    for result in results:
        out, err = result.get()
        logger.debug("out: {} err: {}".format(out, err))


def run_jobs_sge(cmd, cmd_iter_substr, out_dir, err_dir, runs):
    """
    Run jobs using a Sun Grid Engine (SGE) cluster.

    :param cmd: the full command to run as a job
    :param cmd_iter_substr: the substring in command to be replaced with a number
    :param out_dir: the directory containing the standard output from qsub
    :param err_dir: the directory containing the standard error from qsub
    :param runs: the number of runs to execute
    """
    # Test this with echo "ls -la" | xargs xargs using Python environment.
    # The following works:
    # lsCMD = "ls -la"
    # echo_cmd=["echo", lsCMD]
    # xargsCMD=["xargs", "xargs"]
    # echo_proc = subprocess.Popen(echo_cmd, stdout=subprocess.PIPE)
    # xargsProc = subprocess.Popen(xargsCMD, stdin=echo_proc.stdout)
    jobs = ""
    for i in xrange(1, runs + 1):
        # Now the same with qsub
        jobs = "j" + str(i) + "," + jobs
        qsub_cmd = ["qsub", "-cwd", "-V", "-N", "j" + str(i), "-o", os.path.join(out_dir, "j" + str(i)), "-e", os.path.join(err_dir, "j" + str(i)), "-b", "y", cmd.replace(cmd_iter_substr, str(i))]
        qsub_proc = subprocess.Popen(qsub_cmd, stdout=subprocess.PIPE)
        logger.debug(qsub_cmd)
    # Check here when these jobs are finished before proceeding
    # don't add names for output and error files as they can generate errors..
    qsub_cmd = ["qsub", "-sync", "y", "-b", "y", "-o", "/dev/null", "-e", "/dev/null", "-hold_jid", jobs[:-1], "sleep", "1"]
    qsub_proc = subprocess.Popen(qsub_cmd, stdout=subprocess.PIPE)
    qsub_proc.communicate()[0]
    logger.debug(qsub_cmd)


def run_jobs_lsf(cmd, cmd_iter_substr, out_dir, err_dir, runs):
    """
    Run jobs using a Load Sharing Facility (LSF) cluster.

    :param cmd: the full command to run as a job
    :param cmd_iter_substr: the substring in command to be replaced with a number
    :param out_dir: the directory containing the standard output from bsub
    :param err_dir: the directory containing the standard error from bsub
    :param runs: the number of runs to execute
    """
    jobs = ""
    for i in xrange(1, runs + 1):
        jobs = "done(j" + str(i) + ")&&" + jobs
        bsub_cmd = ["bsub", "-cwd", "-J", "j" + str(i), "-o", os.path.join(out_dir, "j" + str(i)), "-e", os.path.join(err_dir, "j" + str(i)), cmd.replace(cmd_iter_substr, str(i))]
        bsub_proc = subprocess.Popen(bsub_cmd, stdout=subprocess.PIPE)
        logger.debug(bsub_cmd)
    # Check here when these jobs are finished before proceeding
    import random
    import string
    job_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(7))
    bsub_cmd = ["bsub", "-J", job_name, "-o", "/dev/null", "-e", "/dev/null", "-w", jobs[:-2], "sleep", "1"]
    bsub_proc = subprocess.Popen(bsub_cmd, stdout=subprocess.PIPE)
    bsub_proc.communicate()[0]
    logger.debug(bsub_cmd)
    # Something better than the following would be highly desirable
    import time
    found = True
    while found:
        time.sleep(2)
        my_poll = subprocess.Popen(["bjobs", "-psr"], stdout=subprocess.PIPE)
        output = my_poll.communicate()[0]
        if job_name not in output:
            found = False
