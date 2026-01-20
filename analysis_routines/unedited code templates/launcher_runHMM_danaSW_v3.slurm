#!/bin/bash -l
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --mem=10g
#SBATCH --tmp=10g
#SBATCH --mail-type=ALL
#SBATCH --mail-user=muel0720@umn.edu
#SBATCH --job-name=StarWarsHMM
#SBATCH --output=StarWarsHMM.o%j
#SBATCH --error=StarWarsHMM.e%j

#This file is set up prior to running "MSI_practice." I don't actually run this file line by line. "MSI_practice" executes it. 

#This is the folder you are inputing
module load python
rclone -v copy "UMNdrive:/Projects/Dana/Dana_StarWars_2022_Dups/bandit_processed/" /scratch.global/muel0720/starwars/bandit_processed/

#This is the telling python to run the code that is already in the scratch for MSI
python /scratch.global/muel0720/starwars/analysis_routines/HMM2ArmAcrossSession_dm_221219.py

#This is telling rclone to please take the output it got from MSI and put it in my actual google drive folder
rclone -v copy /scratch.global/muel0720/starwars/HMM_output/ "UMNdrive:/Projects/Dana/Dana_StarWars_2022_Dups/HMM_output/"
