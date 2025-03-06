#!/usr/bin/env bash
#SBATCH -J molpro
#SBATCH --nodes=1
#SBATCH -n 12
#SBATCH --time 2-00:00:00
#SBATCH --mem=376GB
#SBATCH --gres=scratch:1024

module purge

module load chem/molpro/2024.1.0

molpro -m 4000 molpro.inp
