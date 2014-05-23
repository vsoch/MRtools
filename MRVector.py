#!/usr/bin/env python2

"""

MRVector --> Mask and Extract timeseries from list of MR images

This script will read in a list of images, a list of masks, and output a .mat file
for manipulation of raw data in matlab.  In the future, this could all be done using
MRtools, or pyML.

NOTES:
1) **IMAGES MUST BE EQUALLY SIZED AND REGISTERED TO SAME SPACE**
2) MRV.cleanup() is on by default to eliminate features that are 0 for all subjects
   To return complete brain data for everyone, comment out "MRV.cleanup()" in main


INPUT:
-h, --help      Print this usage
-i --img=       Single column text file w/ list of images
-m --mask=      Single column text file w/ list of masks.  If only 1 image is specified,
                will use for all images.  If > 1, must be equal to number of images
-o --out=       output .mat name "path/to/data.mat" or "data.mat"

USAGE: python MRVector.py --img=imglist.txt --mask=/path/to/masklist.txt --out=data.mat

OUTPUT: .mat file for loading into matlab with the following variables:
        data: a n X m matrix, n rows of images, m columns of features (voxels)
        label: a n X 1 matrix with names of images
        xyz: a 1 X m matrix with xyz coordinates of each voxel

"""

__author__ = "Vanessa Sochat (vsochat@stanford.edu)"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2012/03/17 $"
__license__ = "Python"

import os
import sys
import MRtools # includes classes Data, and Mask 
import numpy as nu
import scipy
import operator
import getopt
import re


# MRVECTOR------------------------------------------------------------------------------
class MRVector:
    def __init__(self,img1,mask1):
        self.readImage(img1,mask1)
        self.prepVector()

    # Extract first image
    def readImage(self,img1,mask1):
        # Extract the first image into a Data Object
        self.firstMR = MRtools.Data(img1)

        # Extract the mask into a mask object
        self.firstMSK = MRtools.Mask(mask1) 
        masked = self.firstMSK.applyMask(self.firstMR)

        # Save the size of the image to compare with others
        self.Vlength = self.firstMR.xdim*self.firstMR.ydim*self.firstMR.zdim

    def prepVector(self):
        # Create vector to hold all values
        self.vectors = []

        # Prepare raw xyz labels that correspond with voxels
        self.xyz = []     # MNI 152 labels
        self.labels = []  # image paths
        xyzcount = 0
        for xyz in range(0,nu.shape(self.firstMR.XYZ)[1]):
            self.xyz.append(str(self.firstMR.XYZ[0,xyz]) + "|" + str(self.firstMR.XYZ[1,xyz]) + "|" + str(self.firstMR.XYZ[2,xyz]))
            xyzcount+=1 
        # Since we have 4D data, we need to X by n timepoints
        print "Number TR is " + str(nu.shape(self.firstMR.data)[3])
        self.xyz = self.xyz*nu.shape(self.firstMR.data)[3]
           
        # We will add rows of xyz values in self.vectors
        self.vectors.append(self.firstMR.data.flatten())

        # We will add image names to self.labels
        self.labels.append(self.firstMR.name)
        
    
    # Add vector of data to current vector to print
    def addVectorRow(self,MRtoadd):

        # Make sure that vector is of equal length
        if ((MRtoadd.xdim*MRtoadd.ydim*MRtoadd.zdim) != self.Vlength):
            print "Error: " + MRtoadd + " is of different size than " + self.firstMR
            return
        else: # Flatten the data and add as a row 
            print "Adding data vector for " + MRtoadd.name + "...\n"
            self.vectors = nu.vstack([self.vectors,MRtoadd.data.flatten()])
            # Add image label to labels
            self.labels.append(MRtoadd.name)

    # cleanUp: gets rid of features for which everyone has a value of 0
    def cleanUp(self):
        toremove = []
        print "Eliminating shared values of zero (columns) from matrix..."
        for c in range(0,nu.shape(self.vectors)[1]-1):
            # If sum is == 0, save index to remove column from vectors
            if sum(self.vectors[:,c]) == 0:
                toremove.append(c)   
            
        print "Removing " + str(len(toremove)) + " voxel features..."
        print "Keeping " + str(len(self.xyz)-len(toremove))
        # Remove all empty columns from vectors and xyz
        self.vectors = nu.delete(self.vectors,toremove,1)
        self.xyz = nu.delete(self.xyz,toremove)
        

# USAGE ---------------------------------------------------------------------------------
def usage():
    print __doc__

# Reads single column text file, returns list
def readInput(readfile):
    flist = []
    print "Reading input file " + readfile
    try:
        rfile = open(readfile,'r')
	for line in rfile:
	    flist.append(line.rstrip("\n").rstrip())
        rfile.close()
    except:
        print "Cannot open file " + readfile + ". Exiting"
        sys.exit()
    flist
    return flist

# Check that all image files exist
def checkInput(imginput):
   print "Checking for all images..." 
   for img in imginput:
       if img:
           if not os.path.isfile(img):
                   print "Cannot find " + img + ". Exiting!"
                   sys.exit()
   print "All images have been found!  Continuing analysis..." 
    

# MAIN ----------------------------------------------------------------------------------
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:m:o:", ["help","img=","mask=","out="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    # First cycle through the arguments to collect user variables
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()    
        if opt in ("-i","--img"): images = arg
        if opt in ("-m", "--mask"): mask = arg
        if opt in ("-o", "--out"): output = arg
        
    # Get list of images and mask paths
    imgfiles = readInput(images)
    maskimg = readInput(mask)

    # Check that all image files exist
    checkInput(imgfiles)
    checkInput(maskimg)
        
    # Create MRtools Mask objects
    # Make sure user has specified at least one mask image
    if len(maskimg) == 0:
        print "Error, please specify 1 or more mask images!"
        sys.exit()
    # One mask image specified - use for all images
    elif len(maskimg) == 1: 
        Mask = MRtools.Mask(maskimg)
        masks = []
        for i in range(0,len(imgfiles)-1):
            masks[i] = Mask
    # > 1 mask image specified < total images, not allowed
    elif len(maskimg) != len(imgfiles):
        print "Error, either specify one mask for all images,"
        print "or one mask per image.  Exiting"
        sys.exit()
    # Num mask images ==  total images, one mask / image
    elif len(maskimg) == len(imgfiles):
    
        print "Found " + str(len(imgfiles)) + " images and masks."  
        masks = []
        for i in range(0,len(imgfiles)):
            print maskimg[i]
            onemask = MRtools.Mask(maskimg[i])
            masks.append(onemask)
    

    # Prepare MRVector Object to hold data vectors
    MRV = MRVector(imgfiles[0],maskimg[0])
    
    # MASK EACH IMAGE------------------------------------------------------
    counter = 0   
    for img in imgfiles:
        if img:
            if counter != 0:
            #try:
                # Use MRtools Data class to read in image
                Image = MRtools.Data(img,'4D')
                # Apply mask to Image
                Image = masks[counter].applyMask(Image)
                # Extract values and add to vector with subject ID
                MRV.addVectorRow(Image)
            counter = counter + 1
            #except:
            #    print "Problem with " + img + ". Exiting!"
	    #    sys.exit() 

    print "Finished extracting all image vectors..."
    # Cleanup will remove feature columns that all are 0.  
    # If you do not want cleanup, comment out this function
    MRV.cleanUp()

    # Now we want to save this data to a .mat file
    MRVec = {}
    MRVec['data'] = MRV.vectors
    MRVec['label'] = MRV.labels
    MRVec['xyz'] = MRV.xyz
    scipy.io.savemat(output,MRVec)

if __name__ == "__main__":
    main(sys.argv[1:])
