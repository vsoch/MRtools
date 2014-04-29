#!/usr/bin/env python2

"""

resultReport.py --> Print MRTools Match Report in Python

This python script takes a report produced by pyMatch.py and prints an HTML
report for visually seeing the matched images.

INPUT:
-h, --help      Print this usage
-r --report=    Single text report file (--number=s) OR folder with multiple reports (--number=m)
-t --template=  Path to image to display for template (single), OR path to folder with images (multiple)
-o --oname=     Name for output folder in PWD
-n --number=    s for single report, m for multiple reports in one folder
-e --print matchesthresh=    (optional) a threshold for match scores

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
import numpy as np

# USAGE ---------------------------------------------------------------------------------
def usage():
    print __doc__

# Print HTML report!
def printHTML(output,result,maxscore,maxid,number,thresh=0):
    if not os.path.isfile(output + "/report.html"):
        print "Creating results HTML report in " + output + "..."
        report = open(output + "/report.html",'w')
        report.write("<html>\n<body>\n<h1>MRTools Result Report</h1>\n")
        if number == "s":
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

        # For multiple report, organize by term and top matches
        # dict[term] = [image path||score,imagepath||score,...\
        # If the user doesn't define a threshold, print all, otherwise threshold
        elif number == "m":
          # The main report page will have links to each of the terms
          for term,matches in result.iteritems():
            report.write("<h2><a href=" + term +".html>" + term + "</a></h2>")
            # Write the report page
            page =  open(output + "/" + term + ".html",'w')
            # First print the template image
            page.write("<html>\n<body>\n<h1>" + term.upper() + " Matched Images</h1>\n")
            page.write('<strong>Threshold: Score > ' + str(thresh) + "</strong><br>\n")
            # Print the template image
            page.write("<img src=\"img/" + term + ".png\" /><br>\"\n")
            # Now for each result, print images - order by match score
            paths = []; scores = []
            # If we only have one match
            print matches
            if not isinstance(matches,list):
              pathy,score = matches.split("||")
              print "SCORE: " + str(score)
              print "THRESH: " + str(thresh)
              if float(score) > float(thresh):
                print "Adding score " + str(thresh) + " to " + term
                page.write("<p><strong>" + str(score) + "</strong></p>\n")
                page.write("<img src=\"" + pathy + "\" width=\"30%\" />\"")
                page.write("<br /><br />\n")
            else:
              for res in matches:
                pathy,score = res.split('||')
                if float(score) > float(thresh):
                  paths.append(pathy)
                  scores.append(float(score))
              # Order by match score
              idx = [i[0] for i in sorted(enumerate(scores), key=lambda x:x[1])]
              paths = [paths[i] for i in idx]
              scores = [scores[i] for i in idx]
              for i in range(0,len(paths)):
                pathy = paths[i]
                score = scores[i]
                page.write("<p><strong>" + str(score) + "</strong></p>\n")
                page.write("<img src=\"" + pathy + "\" width=\"30%\" />\"")
	        page.write("<br /><br />\n")
            page.write("</body>\n</html>")
            page.close()  
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


def getFiles(folder,pattern):
  # Get report files in folder
  infiles = []
  for filey in os.listdir(folder):
    if filey.endswith(pattern):
      infiles.append(filey)
  return infiles

# PRINT OUTPUT FOR MULTIPLE FILES IN ONE FOLDER
def readInputMulti(folder):

    # Get report files in folder
    infiles = getFiles(folder,"beststats.txt")

    # We will need to save a dictionary of images
    # For each image, we save the top match score across all maps
    mrs = dict()
    print "Reading " + str(len(infiles)) + " input files..."
    for f in infiles:
      try:
          rfile = open(folder + "/" + f,'r')
          term = f.split(".")[0]
          for line in rfile:
            line = line.rstrip("\n").rstrip(" ").rstrip()
            sub,match1,val1,match2,val2,match3,val3 = line.split(" ")
            if sub not in ("ID"):
            # If we've already seen the subject
              if sub in mrs:
                topmatch = mrs[sub]
                tmp,maxscore = topmatch.split('||')
                if float(val1) >= float(maxscore): mrs[sub + "/" + match1] = term + "||" + val1
                if float(val2) >= float(maxscore): mrs[sub + "/" + match2] = term + "||" + val2
                if float(val3) >= float(maxscore): mrs[sub + "/" + match3] = term + "||" + val3
              # If we haven't seen this subject
              else:
                vals = [float(val1),float(val2),float(val3)]
                mrtmp = [match1,match2,match3]
                # Get index of the top value
                idx = sorted(range(len(vals)), key=lambda i: vals[i])[-1:]
                # Save to dictionary
                mrs[sub + "/" + mrtmp[idx[0]]] = term + "||" + str(vals[idx[0]])
          rfile.close()
      except:
          print "Cannot open file " + f + ". Exiting"
          sys.exit()
      
    # At this point, we have a dictionary of component image paths, each matched to a top term
    return mrs

# Get full paths for components and subject folders
def fullPaths(result,number):
    
    # If we are doing a single result file run:
    if number == "s":
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
  
    # If we are doing a multiple report
    elif number == "m":
      # result is a dictionary
      # Index is component full path, value is term||topscore
      # We need to return a new dictionary with png paths instead of .nii.gz
      resultpng = dict()
      for mr,val in result.iteritems():
        
        # Extract the thresh_zstat number and match to the report png image
        znumexp = re.compile('[0-9]{1,2}')
        component = mr.split('/')[-1]
        znum = znumexp.search(component)
        znumber = component[znum.start():znum.end()]
	
        # Now get the folder path
        ica = re.compile(".ica")
	matches = [(m.start(0), m.end(0)) for m in ica.finditer(mr)]
	
        # Replace this path with the path to the subject report folder, image
        png = mr[0:matches[len(matches)-1][1]] + "/report/IC_" + znumber + "_thresh.png"
        resultpng[png] = val
      return resultpng  

# Reorganize dictionary of dict[image path] = term||score to --> dict[term] = [image path||score,imagepath||score,...\
def termMatch(pngs):
   finalres = dict()
   for mrpath,val in pngs.iteritems():
     term,score = val.split('||')
     if term not in finalres:
       finalres[term] = mrpath + '||' + score
     else:
       holder = finalres[term]
       if not isinstance(holder,list):
         holder = [holder, mrpath + '||' + score]
       else:
         holder.append(mrpath + '||' + score)
       finalres[term] = holder
   return finalres

def setupOut(output,tempimg,result,infile,number):
    # Create output directory, if doesn't exist
    if not os.path.exists(output):
        os.makedirs(output)
    if not os.path.exists(output + "/img"):
        os.makedirs(output + "/img")
    
    # Copy each subject image into the image folder, number subjects 1 to N
    count = 0
    if number == "s":
      if os.path.isfile(infile):
        shutil.copy(infile,output + "/result.txt")
      if os.path.isfile(tempimg):
        shutil.copy(tempimg,output + "/img/template.png")
      else:
        print "Cannot find " + tempimg + ". Exiting!"
        sys.exit()

      for res in result:
          for i in [1,3,5]:
              shutil.copy(res[0] + "/report/" + res[i],output + "/img/" + str(count + 1) + res[i]) 
	      result[count][i] = "img/" + str(count + 1) + res[i]
	  count = count + 1

    # If we have done analysis for multiple, just copy the images
    elif number == "m":
      count = 0
      finalpaths = dict()
      for png, val in result.iteritems():
        shutil.copy(png,output + "/img/" + str(count + 1) + png.split('/')[-1]) 
        finalpaths["img/" + str(count + 1) + png.split('/')[-1]] = val
        count = count + 1
      result = finalpaths
      # Also copy template images, they are in "tempimg" directory
      imgfiles = getFiles(tempimg,".png")
      for i in imgfiles:
        shutil.copy(tempimg + "/" + i,output + "/img/" + i) 
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
        if opt in ("-e","--thresh"):
            number = arg


    if number.lower() not in ("s","m"):
      usage()
      print "ERROR: Please specify s (single) or m (multiple) for report type"
      sys.exit(32)

    if number == "s":
      # Read in text file input
      print "Generating single report..."
      rawres,maxscore,maxid = readInputSingle(input1)
      # Convert image paths to .png paths
      pathres = fullPaths(rawres,number)
      # Setup output folders and images
      linkres = setupOut(output,tempimg,pathres,input1,number)
      # Print HTML report
      printHTML(output,linkres,maxscore,maxid,number)

    elif number == "m":
      print "Generating multiple file report..."
      # This returns a dictionary, index is component, val is term||maxscore
      mrs = readInputMulti(input1)
      # Convert image paths to .png paths
      pngs = fullPaths(mrs,number)
      # Setup output folders and images
      linkres = setupOut(output,tempimg,pngs,input1,number)
      # Assign each component to its top matched term
      finalres = termMatch(linkres)
      # Print HTML report
      printHTML(output,finalres,999,'None',number,0)

if __name__ == "__main__":
    main(sys.argv[1:])
