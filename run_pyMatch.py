#!/python-lapack-blas/bin/python

import os

# Here we can generate thresh_zstat list
filey = open('images.txt','w')
for i in range(1,101):
  filey.writelines('thresh_zstat' + str(i) + ".nii.gz\n")
filey.close()

#-s --subs=      Single column text file w/ list of subject (or group) folders containing components
subs = "/home/vsochat/SCRIPT/python/MRtools/input.txt"
images = "/home/vsochat/SCRIPT/python/MRtools/images.txt"
templatedir = "/scratch/users/vsochat/DATA/BRAINMAP/nsynth3000"
outdir = "/scratch/users/vsochat/DATA/BRAINMAP/output/PerOverlap"

# Read in templates
templates = open('templates.txt','r').readlines()

# Cycle through templates, calculate match scores for all subjects, for each
for temp in templates:
  tmp = temp.strip("\n")
  template = templatedir + "/" + tmp
  fname = outdir + "/" + tmp.strip('.gz') + "_bestcomps.txt"
  if not os.path.isfile(fname):
    # Create a script to submit job
    filey = open('.jobs/' + tmp + '.job','w')
    filey.writelines("#!/bin/bash\n")
    filey.writelines("#SBATCH --job-name=" + tmp + "\n")  
    filey.writelines("#SBATCH --output=.out/" + tmp + ".out\n")  
    filey.writelines("#SBATCH --error=.out/" + tmp + ".err\n")  
    filey.writelines("#SBATCH --mem=8000\n")
    filey.writelines("/home/vsochat/python-lapack-blas/bin/python pyMatch.py --template=" + template + " --images=" + images + " --subs=" + subs + " --output=" + outdir)
    filey.close()
    os.system("sbatch .jobs/" + tmp + ".job")

