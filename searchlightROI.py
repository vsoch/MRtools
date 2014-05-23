#!/usr/bin/env python2

"""

searchlightROI --> Extract ROI coordinates for superthreshold neighborhoods

This script takes as input a user specified threshold to apply to an input image,
and looks voxelwise across the brain for voxels that surpass this threshold.  
When a voxel is found, the coordinates of the voxel (we might call a centroid)
and its surrounding voxels within a particular distance from both sides (in voxels) 
are extracted. Currently, the script will extract a cube of voxels, however 
functionality might be added to extract different shapes.  Output is N space
delimited text files, each representing one ROI with a list of voxel coordinates
(x y z), one coordinate per line, in the following format:

x1, y1, z1
x2, y2, z2
x3, y3, z3

The centroid is on the first line.

INPUT:
-h, --help      Print this usage
-i --img=       single image to extract
-o --out=       prefix for output file(s)
-t --thresh=    threshold to apply to images
-y --type=      type of ROI (currently square only option)
-s --size=      size of ROI (units from centroid on each side)

USAGE: python searchlightROI.py --img=img.nii.gz --out=path/to/pre --thresh=0.5 --type=square --size=2

OUTPUT: myimage_1.roi ... myimage_N.roi

"""

__author__ = "Vanessa Sochat (vsochat@stanford.edu)"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2012/03/29 $"
__license__ = "Python"

import os
import sys
import MRtools # includes classes Data, and ROI 
import numpy as nu
import scipy
import operator
import getopt
import re


# USAGE ---------------------------------------------------------------------------------
def usage():
    print __doc__

# Check that all image files exist
def checkInput(imginput):
   print "Checking for " + str(imginput) 
   if imginput:
       if not os.path.isfile(imginput):
           print "Cannot find " + imginput + ". Exiting!"
           sys.exit()
   return imginput

# Print lists to text files
def printList(ROIS,outfile):
    N = 1
    fileall = open(outfile + "_all" + ".roi",'w')
    for roi in ROIS:
        # Open file for writing
        fopen = open(outfile + "_" + str(N) + ".roi",'w')
        for coord in roi:
            fopen.writelines(str(coord) + "\n")
        fopen.close()
        N = N +1
    noDups = ridDups(ROIS)
    for coord in noDups:
       fileall.writelines(str(coord) + "\n")
    fileall.close()

def ridDups(array):
    uniques = []
    for e in array:
        for o in e:
            if o not in uniques:
                uniques.append(o)
    return uniques    
    

# MAIN ----------------------------------------------------------------------------------
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:t:o:s:y:", ["help","img=","thresh=","out=","size=","type="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    # First cycle through the arguments to collect user variables
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()    
        if opt in ("-i","--img"): image = arg
        if opt in ("-t", "--thresh"):  thresh = float(arg)
        if opt in ("-o", "--out"): output = arg
        if opt in ("y", "--type"): roitype = arg.lower()
        if opt in ("-s","--size"): 
            if int(arg) <= 0: 
                print "Error, please specify integer size > 0!"
                sys.exit()
            else: size = int(arg)
        
    # Check that all image files exist
    imgfile = checkInput(image)
        
    # Prepare MRtools Data object
    img = MRtools.Data(imgfile)

    # Prepare MRtools ROI Object
    ROI = MRtools.ROI(thresh,size,output)
    
    if roitype == "square":
        voxCOORD,voxRCP = ROI.applySquareROI(img)
    else:
        print "ROI type " + str(roitype) + " currently not supported."
        sys.exit()

    # Print ROI entries to individual text files
    printList(voxCOORD,output + ".xyz")
    printList(voxRCP,output + ".rcp")

if __name__ == "__main__":
    main(sys.argv[1:])
