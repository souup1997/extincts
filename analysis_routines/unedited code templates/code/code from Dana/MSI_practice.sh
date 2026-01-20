#once in MSI, here's what I'm doing to run the code... 
#This code is set up after "launcher_runHMM_danaSW_v3." This is the file I actually run. 

#This makes sure that I am in the right terminal type-- inside MSI
ssh muel0720@mesabi.msi.umn.edu

#Brings me into the scratch folder
cds 

#rclone is nice enought to copy the folder over to scratch from my google drive
rclone -v copy "UMNdrive:/Projects/Dana/Dana_EphysBehavior_2023/analysis_routines/" /scratch.global/muel0720/ephys/analysis_routines/
mkdir -p ephys/HMM_output

#Now we want to step into the output folder so that all outputs will be in the same place.
cd ephys/HMM_output
#Run the code that from the folder you moved into scratch in line 11. Now the "launcher" file takes over.
sbatch /scratch.global/muel0720/ephys/analysis_routines/MSI_launcher/launcher_runHMM_danaSW_v3.slurm

#done.

#If I want to see that it is working: 
squeue --format="%.18i %.9P %.30j %.8u %.8T %.10M %.9l %.6D %R" --me

#so Erin can look at my folder: 
cd /scratch.global/
chmod -R 770 muel0720
ls -1h

