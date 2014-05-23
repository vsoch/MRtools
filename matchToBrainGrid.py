#!/bin/python

# This script will match a set of input functional networks to the brainGrid (SOM Map)
# and output vectors of similarity scores to generate an image of the "behavioral signature"
# TODO: Make R script that takes feature input vector, loads SOM, outputs the visualization

# Just print command
# srun -n 12 -N 1 --mem=64000 --pty bash --
# cd /home/vsochat/SCRIPT/python/MRtools
# source /home/vsochat/python-lapack-blas/bin/activate
# python

import pyMatch
import os.path
import numpy
import MRtools
import sys

temp = sys.argv[1] # temp: is the template image, full path
subs = sys.argv[2] 
images = sys.argv[3]
templatedir = sys.argv[4]
outdir = sys.argv[5]

subfile = pyMatch.readInput(subs)
imgfiles = pyMatch.readInput(images)
found = pyMatch.checkInput(subfile,imgfiles)

# Make full image paths
imgs = list()
for pathy,images in found.iteritems():
  for img_current in images:
    if img_current:
      imgs.append(img_current)

# STOPPED HERE - need to test this, write to matrix with score,
# IMAGES WERE WRONG SIZES - NOW IS FIXED
# make sure that we have the right column names, and then
# write an R script to take a row as input, output mapping to SOM
matrix = list()
tmp = temp.strip("\n")
path, filename = os.path.split(tmp)
fname = outdir + filename.strip('.gz')
if not os.path.isfile(fname):
  Template = MRtools.Data(tmp,'3D')
  Match = MRtools.Match(Template)        # Create an MRTools Match object to do the job!
  Match.setIndexCrit('>',0)              # Set criteria for filtering the template image
  Match.genIndexMNI()                    # Generate the indices based on specified filt
  Match.components = imgs
  print "Computing similarity scores..."    
  resultitem = Match.matchOverlapMatrix() # outputs a dictionary of match scores, each to template
    
  # Now we should prepare output matrix
  rownames = resultitem.keys()

  Result = pyMatch.pyMatchRes(outdir,fname)
  Result.writeHeader(filename.strip('gz') + ":template")

  # For each match score, add to output file
  for i,score in resultitem.iteritems():
    print "Adding " + i + " " + str(score)
    Result.addResult(i + "\t" + str(score))

