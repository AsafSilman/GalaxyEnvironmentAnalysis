import os
from subprocess import check_output, Popen, PIPE, STDOUT

SLURM_SCRIPT_TEMPLATE = \
"""#!/bin/sh
#SBATCH -N 1      # nodes requested
#SBATCH -n 1      # tasks requested
#SBATCH --mem={1}G  # memory in Mb
#SBATCH --partition={2}
#SBATCH -o outfile-{0}  # send stdout to outfile
#SBATCH -e errfile-{0}  # send stderr to errfile
{5}
#SBATCH -J gea-training

cd {3}
source env/bin/activate
{4}
"""

def get_training_command(model_name):
    return f'python gea.py run-experiment "{model_name}"'

def get_job_dependencies_on_partition(partition):
    command = [
        "squeue",
        "--noheader",
        f"--partition={partition}",
        "--format=\"%i\""
    ]
    output = check_output(command).decode().split("\n")
    jobs =  list(
        map(
            lambda x: x.replace("\"", ""),
            filter(
                lambda x: x!="", output
            )
        )
    )
    if jobs:
        return "#SBATCH -d afterok:" + ",".join(jobs)
    else:
        return "#SBATCH --comment=\" \""

def get_slurm_script(model_name, mem_limit_gb=40, partition="mlgpu", project_directory="~/GalaxyEnvironmentAnalysis"):
    training_command = get_training_command(model_name)
    running_jobs = get_job_dependencies_on_partition(partition)
    
    return SLURM_SCRIPT_TEMPLATE.format(
        model_name,
        mem_limit_gb,
        partition,
        project_directory,
        training_command,
        running_jobs
    )

def submit_job_slurm(model_name, **kwargs):
    script = get_slurm_script(model_name, **kwargs)
    
    p = Popen(["sbatch"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    output = p.communicate(input=script.encode())[0]

    return_code = p.wait()
    if return_code == 0:
        return True
    else:
        print(output.decode())
        return False
