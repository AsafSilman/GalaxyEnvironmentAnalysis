#!/bin/sh
#SBATCH -N 1      # nodes requested
#SBATCH -n 1      # tasks requested
#SBATCH -c 10      # cores requested
#SBATCH --mem=180G  # memory in Mb
#SBATCH --partition=mlgpu
#SBATCH -o outfile-TID-ISO  # send stdout to outfile
#SBATCH -e errfile-TID-ISO  # send stderr to errfile

cd ~/GalaxyEnvironmentAnalysis
source env/bin/activate
python gea.py --debug train config/1.0-TID-ISO.yml --new-model
