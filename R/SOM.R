# This script will read in match scores of the ICA components to the SOM 
# templates, save the matrix, and then use the matrix to render
# the SOM map

# Here is how to make the self organizing map
library('kohonen')
library("Rniftilib")

#Path to raw 525 neurosynth maps
mrpath = "/home/vanessa/Documents/Work/NEUROSYNTH/brainmaps525"
mrs = list.files(mrpath,full.names=TRUE)
nsyn525 = matrix(nrow=length(mrs),ncol=902629)

# Read in each file to a matrix
for (i in 1:length(mrs)){
  cat(i,"of",length(mrs))
  m = mrs[i]
  nii = nifti.image.read(m,read_data=1)
  niivector = as.vector(nii[,,,1])
  nsyn525[i,] = niivector
}
# Get rid of path for labels
labels = gsub("/home/vanessa/Documents/Work/NEUROSYNTH/brainmaps525/","",mrs)
rownames(nsyn525) = mrs 

# Save raw data matrix
save(nsyn525,file="/home/vanessa/Documents/Work/NEUROSYNTH/nsyn525Matrix.Rda")

# Create self organizing map
som = som(Xtraining, grid = somgrid(5, 5, "hexagonal"))

library('RColorBrewer')
setwd('/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/icaMatch/SZOHC1610')

# These have matching scores of the ICA components to the SOM templates
inputfiles = list.files('/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/icaMatch/SZOHC1610',pattern="2mm*")
tmp = read.csv(file=inputfiles[1],skip=1,head=FALSE,sep="\t")

data = array(dim=c(dim(tmp)[1],length(inputfiles)))
rownames(data) = as.character(tmp$V1)
colnames(data) = as.character(inputfiles)

# Fill in the data matrix
for (f in inputfiles){
  tmp = read.csv(file=f,skip=1,head=FALSE,sep="\t")
  data[as.character(tmp$V1),f] = tmp$V2
}

save(brainMap,file = '/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/som/brainMap.Rda')

# Load the SOM,labels
load('/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/som/brainMap.Rda')
load('/scratch/users/vsochat/DATA/BRAINMAP/dimensionality_reduction/icaMatch/SZOvsHCMatrix.Rda')

# We need to define a color scale that indicates the strength of the match score
colorscale = brewer.pal(9,"YlOrRd")
colorscale = colorRampPalette(brewer.pal(8,"YlOrRd"))(100)

# The coordinates in so$grid$pts that we plot match the image names, so we need to order the matrix
# by the filename.  First extract the numbers
#imageNames = colnames(data)
#imageNames = as.numeric(gsub("_beststats.txt","",gsub("2mmbrainGrid","",imageNames)))
#idx = sort(imageNames,index.return=TRUE)
#data = data[,colnames(data)[idx$ix]]

# This is our color palette
rbPal <- colorRampPalette(brewer.pal(8,"YlOrRd"))

# This is match scores for one compobent to all images - the range is the max match score for all images
test = data[1,]
test = c(0,as.numeric(test),max(data))

#This adds a column of color values
# based on the y values
color = rbPal(10)[as.numeric(cut(test,breaks = 10))]
color = color[-c(1,508)]

plot(brainMap$som$grid$pts,main="Which BrainTerms Maps are Similar?",col=color,xlab="Nodes",ylab="Nodes",pch=15,cex=6)
text(brainMap$som$grid$pts,brainMap$labels,cex=.6)



### Draw plot of counts coloured by the 'Set3' pallatte
br.range <- seq(min(rand.data),max(rand.data),length.out=10)
results <- sapply(1:ncol(rand.data),function(x) hist(rand.data[,x],plot=F,br=br.range)$counts)
plot(x=br.range,ylim=range(results),type="n",ylab="Counts")
cols <- brewer.pal(8,"Set3")
lapply(1:ncol(results),function(x) lines(results[,x],col=cols[x],lwd=3))

### Draw a pie chart
table.data <- table(round(rand.data))
cols <- colorRampPalette(brewer.pal(8,"YlOrRd"))(100)
pie(table.data,col=cols)


plot(so)
