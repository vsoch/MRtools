#!/bin/python

# run_matchToBrainGrid will create jobs to submit on sherlock cluster to calculate overlap scores

import os

# Read in templates
# Generated with ls /scratch/users/vsochat/DATA/BRAINMAP/nsynth525 -1 >> templates525.txt
templates = open('/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/som/som504/som504images.txt','r').readlines()


subs = "/home/vsochat/SCRIPT/python/MRtools/input.txt"                                               # These are the input ICA directories
images = "/home/vsochat/SCRIPT/python/MRtools/images.txt"                                            # These are input ICA images
templatedir = "/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/som/som504"             # brainGrid Image Directory
outdir = "/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/icaMatch/SZOHC1610/"  # We are calculating percent overlap

for temp in templates:
  path, filename = os.path.split(temp)
  jobby = open(".jobs/" + filename + ".job",'w')
  jobby.writelines("#!/bin/bash\n")
  jobby.writelines("#SBATCH --job-name=" + filename + "\n")  
  jobby.writelines("#SBATCH --output=.out/" + filename + ".out\n")
  jobby.writelines("#SBATCH --error=.out/" + filename + ".err\n")
  jobby.writelines("#SBATCH --time=2-00:00\n")
  jobby.writelines("#SBATCH --mem=8000\n")
  jobby.writelines("python /home/vsochat/SCRIPT/python/MRtools/matchToBrainGrid.py" + " " + temp + " " + subs + " " + images + " " + templatedir + " " + outdir)
  jobby.close()
  os.system("sbatch" + ".jobs/" + filename + ".job")

python matchToBrainGrid.py 
