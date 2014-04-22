#!/usr/bin/env python2

"""

resultReport.py --> Print MRTools Match Report in Python

This python script takes a report produced by pyMatch.py and prints an HTML
report for visually seeing the matched images.

INPUT:
-h, --help      Print this usage
-r --report=    Single text report file (--number=s) OR folder with multiple reports (--number=m)
-t --template=  Path to image to display for template
-o --oname=     Name for output folder in PWD
-n --number     s for single report, m for multiple reports in one folder

USAGE: python resultReport.py --report=thresh_zstat1.nii_beststats.txt --template=/path/to/image.png --oname=thresh1

OUTPUT: report.html and images in oname directory in pwd

"""

__author__ = "Vanessa Sochat (vsochat@stanford.edu)"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/4/19 $"
__license__ = "Python"

import os
import sys
import re
import shutil
import operator
import getopt

# USAGE ---------------------------------------------------------------------------------
def usage():
    print __doc__

# Print HTML report with motion charts for flagged subjects
def printHTML(output,result,maxscore,maxid):
    if not os.path.isfile(output + "/report.html"):
        print "Creating results HTML report in " + output + "..."
        report = open(output + "/report.html",'w')
        report.write("<html>\n<body>\n<h1>MRTools Result Report</h1>\n")
        report.write("<a href=\"result.txt\">Text Report</a>")
        report.write("<p><strong>Template: </strong>: " + output + "</p>\n")
	
	# Print the template image
        report.write("<img src=\"img/template.png\" /><br>\"\n")
	
        # Cycle through list of results, print name and links to component images:
        report.write("<strong>Top Score: " + str(maxscore) + " Image: " + str(maxid) + "\n")
        report.write("<h1>Top Three Matched Components per Subject</h1>\n<p>")
        for res in result:
	    report.write("<p><strong>" + res[0] + "</strong></p>\n")
	    for i in [1,3,5]:
	        report.write("<img src=\"" + res[i] + "\" width=\"30%\" />\"")
	    report.write("<br /><br />\n")
            report.write("Matching Scores: <strong>1)</strong> " + str(res[2]) + " <strong>2)</strong> " + str(res[4]) + "<strong> 3) </strong> " + str(res[6])) 
            report.write("<br /><br />\n")
    

        report.write("</body>\n</html>")
        report.close()

# PRINT OUTPUT FOR ONE TEMPLATE FILE
# Reads single column text file, returns list
def readInputSingle(readfile):
    result = []
    print "Reading single input file " + readfile
    maxscore = 0
    maxid = None
    try:
        rfile = open(readfile,'r')
	for line in rfile:
	    line = line.rstrip("\n").rstrip(" ").rstrip()
	    sub,match1,val1,match2,val2,match3,val3 = line.split(" ")
            if sub not in ("ID"):
                result.append([sub.rstrip(),match1.rstrip(),val1.rstrip(),match2.rstrip(),val2.rstrip(),match3.rstrip(),val3.rstrip().rstrip("\n")])
                if val1 >= maxscore: maxscore = val1; maxid = sub
                if val2 >= maxscore: maxscore = val2; maxid = sub
                if val3 >= maxscore: maxscore = val3; maxid = sub
        rfile.close()
    except:
        print "Cannot open file " + readfile + ". Exiting"
        sys.exit()
    return result,maxscore,maxid

# PRINT OUTPUT FOR MULTIPLE FILES IN ONE FOLDER
def readInputMulti(folder):

    # Get report files in folder
    infiles = []
    for filey in os.listdir(folder):
      if filey.endswith("beststats.txt"):
        infiles.append(filey)

    # We will need to save a dictionary of images
    # For each image, we save the top match score across all maps
    mrs = dict()
    print "Reading " + str(len(infiles)) + " input files..."
    for f in infiles:
      try:
          result = []
          rfile = open(folder + "/" + f,'r')
          term = f.split("_")[0]
            for line in rfile:
              line = line.rstrip("\n").rstrip(" ").rstrip()
              sub,match1,val1,match2,val2,match3,val3 = line.split(" ")
            if sub not in ("ID"):
              # If we've already seen the subject
              if sub in mrs:
                topmatch = mrs[sub]
                tmp,maxscore = topmatch.split('||')
                if val1 >= maxscore: mrs[sub] = term + "||" + val1
                if val2 >= maxscore: maxscore = term + "||" + val2
                if val3 >= maxscore: maxscore = term + "||" + val3
          rfile.close()
      except:
          print "Cannot open file " + f + ". Exiting"
          sys.exit()
      
      # At this point, we have a dictionary of subjects, each matched to a top term
      # NEXT PRINT REPORT TAT DISPLAYS COMPONENT AND IMAGES!
      return result,maxscore,maxid

    

# Get full paths for components and subject folders
def fullPaths(result):
    # result[n][0] is the subject ID
    # result[n][1] -- first match name, result[n][2] -- first match value
    # result[n][3] -- second match name, result[n][4] -- second match value
    # result[n][5] -- third match name, result[n][6] -- third match value
    count = 0
    
    # First fix the subject folder path
    for res in result:
        # First grab the path up to the subject .ica folder
	ica = re.compile(".ica")
	matches = [(m.start(0), m.end(0)) for m in ica.finditer(res[0])]
	
        # Replace this path with the path to the subject report folder        
	result[count][0] = res[0][0:matches[len(matches)-1][1]]
        
        # Now extract the thresh_zstat number and match to the report png image
        for i in [1,3,5]:
            znumexp = re.compile('[0-9]{1,2}')
            znum = znumexp.search(res[i])
            znumber = res[i][znum.start():znum.end()]
	    result[count][i] = "IC_" + znumber + "_thresh.png"
        count = count + 1

    # Return the result with all partial paths
    return result

def setupOut(output,tempimg,result,infile):
    # Create output directory, if doesn't exist
    if not os.path.exists(output):
        os.makedirs(output)
    if not os.path.exists(output + "/img"):
        os.makedirs(output + "/img")
    if os.path.isfile(infile):
        shutil.copy(infile,output + "/result.txt")
    if os.path.isfile(tempimg):
        shutil.copy(tempimg,output + "/img/template.png")
    else:
        print "Cannot find " + tempimg + ". Exiting!"
        sys.exit()

    # Copy each subject image into the image folder, number subjects 1 to N
    count = 0
    for res in result:
        for i in [1,3,5]:
            shutil.copy(res[0] + "/report/" + res[i],output + "/img/" + str(count + 1) + res[i]) 
	    result[count][i] = "img/" + str(count + 1) + res[i]
	count = count + 1

    return result

# MAIN ----------------------------------------------------------------------------------
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hr:o:t:n:", ["help","report=","oname=","template=","number="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    # First cycle through the arguments to collect user variables
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()    
        if opt in ("-r","--report"):
            input1 = arg
        if opt in ("-o","--oname"):
            output = arg
        if opt in ("-t","--template"):
            tempimg = arg
        if opt in ("-n","--number"):
            number = arg

    if number not in ("s","n"):
      usage()
      print "ERROR: Please specify s (single) or m (multiple) for report type"
      sys.exit(32)

    if number == "s":
      # Read in text file input
      print "Generating single report..."
      rawres,maxscore,maxid = readInputSingle(input1)
    elif number == "m":
      print "Generating multiple file report..."
      rawres,maxscore,maxid = readInputMulti(input1)

    # Convert image paths to .png paths
    pathres = fullPaths(rawres)

    # Setup output folders and images
    linkres = setupOut(output,tempimg,pathres,input1)

    # Print HTML report
    printHTML(output,linkres,maxscore,maxid)

if __name__ == "__main__":
    main(sys.argv[1:])
