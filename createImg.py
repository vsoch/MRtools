#!/usr/bin/env python2

from os import listdir
from os.path import isfile, join
import MRtools
import os.path

# This script will use MRtools to create png images of brain maps
indir = "/scratch/users/vsochat/DATA/BRAINMAP/nsynth3000"
images = [ f for f in listdir(indir) if isfile(join(indir,f)) ]
outdir = "/scratch/users/vsochat/DATA/BRAINMAP/img"

for i in images:
   filey = outdir + "/" + i.replace(".nii.gz",".png")
   if not os.path.isfile(filey):
     img = MRtools.Print(indir + "/" + i,outdir + "/" + i.replace(".nii.gz",".png"))
     img.png()


