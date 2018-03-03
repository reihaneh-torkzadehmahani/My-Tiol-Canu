import sys, getopt
from toil.job import Job
from toil.common import Toil
import os
import subprocess
#import sh
import urllib

CanuBinDir ='/home/ubuntu/canu/Linux-amd64/bin'
CanuOptions ="-p ecoli -d ecoil-oxford2 genomeSize=4.8m corMinCoverage=0 corMaxEvidenceErate=0.22 -nanopore-raw oxford.fasta"


def getArgs (job, argv):
	
	try:
		opts, args = getopt.getopt(argv,"hc:o:",["canu-bin-dir=","canu-options="])
	except getopt.GetoptError:
		print "ToilCanu.py -c '''<canu bin directory>''' -o '<canu options>'"
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print "ToilCanu.py -c '''<canu bin directory>''' -o '<canu options>'"
	        	sys.exit()
	      	elif opt in ("-c", "--canu-bin-dir"):
	         	global CanuBinDir
			CanuBinDir = arg
      		elif opt in ("-o", "--canu-options"):
			global CanuOptions
         		CanuOptions = arg
	DD = Job.wrapJobFn(DownloadData)
    	job.addFollowOn(DD)
#--------------------------------------------------------------------------------------------------#    
#def executeJob(job,commandName, currentJob, nextJob):
#        os.chdir('/home/ubuntu/canu/Linux-amd64/bin/')
#        cmd = commandName
#        os.system(cmd)
#        job.fileStore.logToMaster("MerylConfigure job is DONE! ")
#        MCh = Job.wrapJobFn(MerylCheck)
#        job.addFollowOn(MCh)
#--------------------------------------------------------------------------------------------------#
def DownloadData(job,memory="2G", cores=2, disk="2G" ):
    os.chdir(CanuBinDir)
    url = "http://nanopore.s3.climb.ac.uk/MAP006-PCR-1_2D_pass.fasta"
    fileName=os.path.join(CanuBinDir, 'oxford.fasta')
    fileName=CanuBinDir+'/oxford.fasta'
    urllib.urlretrieve(url, fileName)
    job.fileStore.logToMaster("Data has been downloaded successfully!")
    CS = Job.wrapJobFn(CanuStart)
#    job.addFollowOn(CS)
# -----------------------------------------------------------------------------------------------#
def CanuStart(job):
        os.chdir(CanuBinDir)
        cmd = './start_canu.pl ' + CanuOptions
        os.system(cmd)

        job.fileStore.logToMaster("First job is DONE! Starting canu ... ")
        MCo = Job.wrapJobFn(MerylConfigure,"correct" )
        job.addFollowOn(MCo)
# -----------------------------------------------------------------------------------------------#  
def MerylConfigure(job, step):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
	
	if (step == "correct"):
		cmd = './merylConfigure.pl correct'
	elif (step == "trim"):
                cmd = './merylConfigure.pl trim'
        elif (step =="assemble"):
                cmd = './merylConfigure.pl assemble'
        
	os.system(cmd)
        job.fileStore.logToMaster("MerylConfigure job is DONE! "+ "( "+ step + ")" )
        MCh = Job.wrapJobFn(MerylCheck, step)
        job.addFollowOn(MCh)
        #executeJob(job,'./merylConfigure.pl correct',"MerylConfigure","MerylCheck")
#-------------------------------------------------------------------------------------------------# 
def MerylCheck(job, step):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
#open file and read parameters (path + merylPath)
	if (step == "correct"):
		content1=0
       		p=0
        	f=open("/tmp/MC1Parameters.txt", "r")
       		content=f.read().splitlines()
        	merylPath=content[0]
        	CanuItMax=int(content[1])
		#write a loop
#                for  index in range(CanuItMax):
		cmd1 = './merylCheck1.pl correct'
       		os.system(cmd1)
		cmd2 = './merylCheck2.pl correct '+ merylPath
                os.system(cmd2)
		f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
		job.fileStore.logToMaster("CCCCCCCCCCCCCCCCCCCC %s  " % content1)
		p= len (content1)-1	
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()
	
        elif (step == "trim"):
		content1=0
 		p=0
        	f=open("/tmp/MC1Parameters.txt", "r")
        	content=f.read().splitlines()
        	merylPath=content[0]
        	CanuItMax=int(content[1])
		###################################################################
                cmd1 = './merylCheck1.pl trim'
       		os.system(cmd1)
		cmd2 = './merylCheck2.pl trim '+ merylPath
                os.system(cmd2)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                job.fileStore.logToMaster("CCCCCCCCCCCCCCCCCCCC %s  " % content1)
                p= len (content1)-1

		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()
	elif (step =="assemble"):
		content1=0
                p=0
                f=open("/tmp/MC1Parameters.txt", "r")
                content=f.read().splitlines()
                merylPath=content[0]
                CanuItMax=int(content[1])
                ###################################################################
                cmd1 = './merylCheck1.pl assemble'
                os.system(cmd1)
                cmd2 = './merylCheck2.pl assemble '+ merylPath
                os.system(cmd2)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                job.fileStore.logToMaster("CCCCCCCCCCCCCCCCCCCC %s  " % content1)
                p= len (content1)-1

                f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()


                #cmd = './merylCheck1.pl assemble'
        	#os.system(cmd)
	# Complete merylCheck2 in a way that just writes the scripts in a file 
	#Define a function which gets a command(processes) and runs it 
	#invoke this fn as much as all processes are added as the child jod
	#Q? How to create dynamic number of child jobs???

######def binaryStringFn(job, depth, message=""):
	#if depth > 0:
        #job.addChildJobFn(binaryStringFn, depth-1, message + "0")
        #job.addChildJobFn(binaryStringFn, depth-1, message + "1")
    #else:
      #  job.fileStore.logToMaster("Binary string: %s" % message)
	#j2 = j1.addChildJobFn(fn, j1.rv())
#######
        job.fileStore.logToMaster("MerylCheck job is DONE! "+ "( "+ step + ")" )
        RS = Job.wrapJobFn(RunScripts, content1, p, step, "MerylCheck" )
        job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------#
def RunScripts (job, PScripts, count, step, fn):
	job.fileStore.logToMaster("RunScripts started execution \n");
       
        job.fileStore.logToMaster("count is %d" % count)
	for x in range(0, count+1):	#RS = Job.wrapJobFn(RunScripts,PScripts, p, step, fn)
        	command=  PScripts[x]
		job.fileStore.logToMaster(command + "is submitted \n")
		job.addChildJobFn(RunScripts2,command, step, fn)
	if (fn =="MerylCheck"):
                        MP = Job.wrapJobFn(MerylProcess, step)
                        job.addFollowOn(MP)
        elif (fn == "Overlap02"):
                        Ov1=Job.wrapJobFn(Overlap0, step,1)
                        job.addFollowOn(Ov1)
	elif (fn == "Overlap0"):
                        Ov1=Job.wrapJobFn(Overlap1, step,2)
                        job.addFollowOn(Ov1)
        elif (step =="correct" and fn == "Overlap12"):
        		Ov1=Job.wrapJobFn(Overlap1, step,1)
                        job.addFollowOn(Ov1)
	elif (step =="correct" and fn == "Overlap1"):
                        Bcl=Job.wrapJobFn(BuildCorrectionLayouts)
                        job.addFollowOn(Bcl)
        elif (step=="trim" and fn == "Overlap12"):
			Ov1=Job.wrapJobFn(Overlap1, step,1)
                        job.addFollowOn(Ov1)
	elif (step=="trim" and fn == "Overlap1"):
                        T=Job.wrapJobFn(TrimReads)
                        job.addFollowOn(T)	
	elif (fn== "GenerateCorrectedReads2"):
                       Dcr = Job.wrapJobFn(GenerateCorrectedReads,1)
                       job.addFollowOn(Dcr)
        elif (fn== "GenerateCorrectedReads"):
                       Dcr = Job.wrapJobFn(DumpCorrectedReads)
                       job.addFollowOn(Dcr)

	elif (step=="assemble" and fn == "Overlap12"):
			Ov1=Job.wrapJobFn(Overlap1, step,1)
                        job.addFollowOn(Ov1)
	elif (step=="assemble" and fn=="Overlap1"):
			R=Job.wrapJobFn(ReadErrorDetectionConfigure)
                	job.addFollowOn(R)
	elif (step=="assemble" and fn=="ReadErrorDetectionCheck2"):
                        Re = Job.wrapJobFn(ReadErrorDetectionCheck,1)
                        job.addFollowOn(Re)
	elif (step=="assemble" and fn=="ReadErrorDetectionCheck"):
			Oe = Job.wrapJobFn(OverlapErrorAdjustmentConfigure)
       			job.addFollowOn(Oe)
	elif (step=="assemble" and fn=="OverlapErrorAdjustmentCheck2"):
                        Oe = Job.wrapJobFn(OverlapErrorAdjustmentCheck,1)
                        job.addFollowOn(Oe)
	elif (step=="assemble" and fn=="OverlapErrorAdjustmentCheck"):
			Uo = Job.wrapJobFn(UpdateOverlapStore)
		        job.addFollowOn(Uo)
        elif (step=="assemble" and fn=="UnitigCheck2"):
                        job.fileStore.logToMaster("Hahaha yughahha \n");
                        CC = Job.wrapJobFn(UnitigCheck,1 )
                        job.addFollowOn(CC)
	elif (step=="assemble" and fn=="UnitigCheck"):
			job.fileStore.logToMaster("Hahaha yughahha \n");
		        CC = Job.wrapJobFn(ConsensusConfigureCheck,2 )
       			job.addFollowOn(CC)
        elif (step=="assemble" and fn =="ConsensusConfigureCheck2"):
                        CC = Job.wrapJobFn(ConsensusConfigureCheck,1)
                        job.addFollowOn(CC)
	elif (step=="assemble" and fn =="ConsensusConfigureCheck"):
			CL = Job.wrapJobFn(ConsensusLoad )
		        job.addFollowOn(CL)
	elif(step=="assemble" and fn=="AlignGFA2"):
                        GO = Job.wrapJobFn(AlignGFA,1)
                        job.addFollowOn(GO)
	elif(step=="assemble" and fn=="AlignGFA"):
			GO = Job.wrapJobFn(GenerateOutputs)
 		        job.addFollowOn(GO)
			
		#job.fileStore.logToMaster(command + "is submitted \n")                
                #command=command.replace ("./", currentDir)
		#command="/home/ubuntu/canu/Linux-amd64/bin/ecoil-oxford2/correction/0-mercounts/meryl.sh 1 > /home/ubuntu/canu/Linux-amd64/bin/ecoil-oxford2/correction/0-mercounts/meryl.000001.out 2>&1"
                #RS = Job.wrapJobFn(RunScripts,PScripts, count-1, step, fn)
#-----------------------------------------------------------------------------------------------#
def RunScripts2(job, Command,step, fn):
	CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
	os.chdir(CanuBinDir)
        if (step == "correct"):
                if (fn=="MerylCheck"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/0-mercounts/'
                        os.chdir(currentDir)
                elif (fn == "Overlap0" or fn =="Overlap02" or fn=="Overlap1" or fn =="Overlap12"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/1-overlapper/'
                        os.chdir(currentDir)
                elif (fn== "GenerateCorrectedReads" or fn== "GenerateCorrectedReads2"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/2-correction/'
                        os.chdir(currentDir)
        elif (step == ("trim")):
                if (fn=="MerylCheck"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/trimming'+ '/0-mercounts/'
                        os.chdir(currentDir)
                elif (fn == "Overlap0" or fn=="Overlap1" or fn =="Overlap12" or fn =="Overlap02" ):
                        currentDir= CanuBinDir + 'ecoil-oxford2/trimming'+ '/1-overlapper/'
                        os.chdir(currentDir)
	elif (step == "assemble"):
		if (fn=="MerylCheck"):
			currentDir= CanuBinDir + 'ecoil-oxford2/unitigging'+ '/0-mercounts/'
                        os.chdir(currentDir)
		elif (fn == "Overlap0" or fn=="Overlap02" or fn=="Overlap1" or fn =="Overlap12"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/unitigging'+ '/1-overlapper/'
                        os.chdir(currentDir)
                elif (fn== "ReadErrorDetectionCheck" or fn== "ReadErrorDetectionCheck2" or fn=="OverlapErrorAdjustmentCheck" or fn=="OverlapErrorAdjustmentCheck2" ):
                        currentDir= CanuBinDir + 'ecoil-oxford2/unitigging'+ '/3-overlapErrorAdjustment/'
                        os.chdir(currentDir)
		elif(fn=="UnitigCheck" or fn=="UnitigCheck2"):
			currentDir= CanuBinDir + 'ecoil-oxford2/unitigging'+ '/4-unitigger/'
                        os.chdir(currentDir)
		elif (fn=="ConsensusConfigureCheck" or fn=="ConsensusConfigureCheck2"):
			job.fileStore.logToMaster("*****************************" )
			currentDir= CanuBinDir + 'ecoil-oxford2/unitigging'+ '/5-consensus/'
                        os.chdir(currentDir)
		
	#os.chdir(CanuBinDir)
	os.system(Command)
        job.fileStore.logToMaster("****************COMMAND*************" + Command )

#------------------------------------------------------------------------------------------------#
def MerylProcess(job, step):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)

	if (step == "correct"):
                cmd = './merylProcess.pl correct'
        elif (step == "trim"):
                cmd = './merylProcess.pl trim'
        elif (step =="assemble"):
                cmd = './merylProcess.pl assemble'

        os.system(cmd)
        job.fileStore.logToMaster("MeryProcess job is DONE! "+ "( "+ step + ")")
        Ov = Job.wrapJobFn(Overlap0, step,2)
        job.addFollowOn(Ov)
# -----------------------------------------------------------------------------------------------#  
def Overlap0(job, step, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)

	if (step == "correct"):
                cmd = './overlap.pl correct0'
		os.system(cmd)
		f1=open("/tmp/ProcessQueue.txt", "r")
		content1=f1.read().splitlines()
                p= len (content1)-1
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()

        elif (step == "trim"):
                cmd = './overlap.pl trim0'
		os.system(cmd)
		f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()


        elif (step =="assemble"):
                cmd = './overlap.pl assemble0'
		os.system(cmd)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1
                f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()
        	
	if (It == 2):
                job.fileStore.logToMaster("Overlap0 job is DONE! "+ "( "+ step + ")")
                RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap02" )
                job.addFollowOn(RS)
        else:
		job.fileStore.logToMaster("Overlap0 job is DONE! "+ "( "+ step + ")")
       		RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap0" )
       		job.addFollowOn(RS)

# -----------------------------------------------------------------------------------------------#
def Overlap1(job, step, It):
	CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)

        if (step == "correct"):
                cmd = './overlap.pl correct1'
                os.system(cmd)
		os.system(cmd)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()

        elif (step == "trim"):
                cmd = './overlap.pl trim1'
                os.system(cmd)
		f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()
               # T=Job.wrapJobFn(TrimReads)
               # job.addFollowOn(T)

        elif (step =="assemble"):
                cmd = './overlap.pl assemble1'
                os.system(cmd)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1
		f1.close();
                open("/tmp/ProcessQueue.txt", 'w').close()
		#R=Job.wrapJobFn(ReadErrorDetectionConfigure)
                #job.addFollowOn(R)
	if (It == 2):
        	job.fileStore.logToMaster("Overlap1 job is DONE! "+ "( "+ step + ")")
        	RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap12" )
        	job.addFollowOn(RS)
	else:
		job.fileStore.logToMaster("Overlap1 job is DONE! "+ "( "+ step + ")")
        	RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap1" )
        	job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------# 
def BuildCorrectionLayouts(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './buildCorrectionLayouts.pl'
        os.system(cmd)
        job.fileStore.logToMaster("BuildCorrectionLayouts job is DONE! ")
        Gcr = Job.wrapJobFn(GenerateCorrectedReads,2)
        job.addFollowOn(Gcr)
# -----------------------------------------------------------------------------------------------# 
def GenerateCorrectedReads(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './generateCorrectedReads.pl'
        os.system(cmd)
	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        job.fileStore.logToMaster("GenerateCorrectedReads job is DONE! ")
	if (It==2):
		RS = Job.wrapJobFn(RunScripts, content1, p, "correct", "GenerateCorrectedReads2" )
        	job.addFollowOn(RS)
	else:
		RS = Job.wrapJobFn(RunScripts, content1, p, "correct", "GenerateCorrectedReads" )
                job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------# 
def DumpCorrectedReads(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './dumpCorrectedReads.pl'
        os.system(cmd)
#	if (It ==2):
#		job.fileStore.logToMaster("DumpCorrectedReads job is DONE! ")
#                BH = Job.wrapJobFn(GenerateCorrectedReads)
#                job.addFollowOn(BH)
#	else:
        job.fileStore.logToMaster("DumpCorrectedReads job is DONE! ")
        BH = Job.wrapJobFn(BuildHTML, "correct")
        job.addFollowOn(BH)
# -----------------------------------------------------------------------------------------------# 
def BuildHTML(job, step):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
	if (step == "correct"):
                cmd = './buildHTML.pl correct'
		os.system(cmd)
	 	G= Job.wrapJobFn(Gatekeeper, "trim")
        	job.addFollowOn(G)

        elif (step == "trim"):
                cmd = './buildHTML.pl trim'
		os.system(cmd)
		G = Job.wrapJobFn(Gatekeeper, "assemble")
        	job.addFollowOn(G)

        job.fileStore.logToMaster("BuildHTML job is DONE! hahahahahah "+ "( "+ step + ")")
# -----------------------------------------------------------------------------------------------# 
# -----------------------------------------------------------------------------------------------#  
def Gatekeeper (job, step):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)

	if (step == "trim"):
        	cmd = './gatekeeper.pl trim'
		os.system(cmd)
	        os.system('cp -rf ecoil-oxford2/trimming/ecoli.gkpStore/ ecoil-oxford2/')
	elif (step =="assemble"):
		cmd = './gatekeeper.pl assemble'

        os.system(cmd)
        job.fileStore.logToMaster("Gatekeeper job is DONE! " + "( "+ step + ")" )
        MCh = Job.wrapJobFn(MerylConfigure, step)
        job.addFollowOn(MCh)
        #executeJob(job,'./merylConfigure.pl correct',"MerylConfigure","MerylCheck")
#-------------------------------------------------------------------------------------------------# 
def TrimReads(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './trimReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("TrimReads job is DONE! ")
        S = Job.wrapJobFn(SplitReads)
        job.addFollowOn(S)
# -----------------------------------------------------------------------------------------------# 
def SplitReads(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './splitReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("SplitReads job is DONE! ")
        D = Job.wrapJobFn(DumpReads)
        job.addFollowOn(D)
# -----------------------------------------------------------------------------------------------#  
def DumpReads(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './dumpReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("DumpReads job is DONE! ")
        B=Job.wrapJobFn(BuildHTML , "trim")
        job.addFollowOn(B)
# -----------------------------------------------------------------------------------------------# 
# -----------------------------------------------------------------------------------------------# 
def ReadErrorDetectionConfigure(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './readErrorDetectionConfigure.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ReadErrorDetectionConfigure job is DONE! ")
	Re = Job.wrapJobFn(ReadErrorDetectionCheck,2)
        job.addFollowOn(Re)
# -----------------------------------------------------------------------------------------------# 
def ReadErrorDetectionCheck(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './readErrorDetectionCheck.pl'
        os.system(cmd)
	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
	f1.close();
        open("/tmp/ProcessQueue.txt", 'w').close()	
	if(It==2):
        	job.fileStore.logToMaster("ReadErrorDetectionCheck job is DONE! ")
		RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "ReadErrorDetectionCheck2" )
        	job.addFollowOn(RS)
	else:
                job.fileStore.logToMaster("ReadErrorDetectionCheck job is DONE! ")
                RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "ReadErrorDetectionCheck" )
                job.addFollowOn(RS)
       # Oe = Job.wrapJobFn(OverlapErrorAdjustmentConfigure)
       # job.addFollowOn(Oe)
# -------------------------------------------e---------------------------------------------------# 
def OverlapErrorAdjustmentConfigure(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './overlapErrorAdjustmentConfigure.pl'
        os.system(cmd)
        job.fileStore.logToMaster("OverlapErrorAdjustmentConfigure job is DONE! ")
        OeA = Job.wrapJobFn(OverlapErrorAdjustmentCheck,2)
        job.addFollowOn(OeA)
# -----------------------------------------------------------------------------------------------# 
def OverlapErrorAdjustmentCheck(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './overlapErrorAdjustmentCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("OverlapErrorAdjustmentCheck job is DONE! ")
	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        f1.close();
        open("/tmp/ProcessQueue.txt", 'w').close()
	if(It==2):
        	job.fileStore.logToMaster("ReadErrorDetectionCheck job is DONE! ")
        	RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "OverlapErrorAdjustmentCheck2" )
        	job.addFollowOn(RS)
	else:
		job.fileStore.logToMaster("ReadErrorDetectionCheck job is DONE! ")
        	RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "OverlapErrorAdjustmentCheck" )
       		job.addFollowOn(RS)
#        Uo = Job.wrapJobFn(UpdateOverlapStore)
#        job.addFollowOn(Uo)
# -----------------------------------------------------------------------------------------------# 
def UpdateOverlapStore(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './updateOverlapStore.pl'
        os.system(cmd)
        job.fileStore.logToMaster("UpdateOverlapStore job is DONE! ")
        U = Job.wrapJobFn(Unitig)
        job.addFollowOn(U)
# -----------------------------------------------------------------------------------------------# 
def Unitig(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './unitig.pl'
        os.system(cmd)
        job.fileStore.logToMaster("Unitig job is DONE! ")
        UC = Job.wrapJobFn(UnitigCheck,2)
        job.addFollowOn(UC)
# -----------------------------------------------------------------------------------------------# 
def UnitigCheck(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './unitigCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("UnitigCheck job is DONE! ")

	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        f1.close();
        open("/tmp/ProcessQueue.txt", 'w').close()
	if(It==2):
        	RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "UnitigCheck2" )
        	job.addFollowOn(RS)
        else:
                RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "UnitigCheck" )
                job.addFollowOn(RS)
#        CC = Job.wrapJobFn(ConsensusConfigureCheck )
#        job.addFollowOn(CC)
# -----------------------------------------------------------------------------------------------# 
def ConsensusConfigureCheck(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './consensusConfigureCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusConfigureCheck job is DONE! ")
		
	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        f1.close();
        open("/tmp/ProcessQueue.txt", 'w').close()
	if(It==2):
        	RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "ConsensusConfigureCheck2" )
        	job.addFollowOn(RS)
        else:
                RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "ConsensusConfigureCheck" )
                job.addFollowOn(RS)
#        CL = Job.wrapJobFn(ConsensusLoad )
#        job.addFollowOn(CL)
# -----------------------------------------------------------------------------------------------# 
def ConsensusLoad(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './consensusLoad.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusLoad job is DONE! ")
        CA = Job.wrapJobFn(ConsensusAnalyze)
        job.addFollowOn(CA)
# -----------------------------------------------------------------------------------------------# 
def ConsensusAnalyze(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './consensusAnalyze.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusAnalyze job is DONE! ")
        A = Job.wrapJobFn(AlignGFA,2)
        job.addFollowOn(A)

# -----------------------------------------------------------------------------------------------# 
def AlignGFA(job, It):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './alignGFA.pl'
        os.system(cmd)
        job.fileStore.logToMaster("AlignGFA job is DONE! ")

	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        f1.close();
        open("/tmp/ProcessQueue.txt", 'w').close()
	if (It ==2):
        	RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "AlignGFA2" )
        	job.addFollowOn(RS)
	else:
                RS = Job.wrapJobFn(RunScripts, content1, p, "assemble", "AlignGFA" )
                job.addFollowOn(RS)
        ##	GO = Job.wrapJobFn(GenerateOutputs)
        #	job.addFollowOn(GO)
# -----------------------------------------------------------------------------------------------# 
def GenerateOutputs(job):
        CanuBinDir='/home/ubuntu/canu/Linux-amd64/bin/'
        os.chdir(CanuBinDir)
        cmd = './generateOutputs.pl'
        os.system(cmd)
        job.fileStore.logToMaster("GenerateOutputs job is DONE! ")

if __name__ == "__main__":
        #options = Job.Runner.getDefaultOptions("./toilWorkflow")
        parser = Job.Runner.getDefaultArgumentParser()
        options = parser.parse_args()
	options.logLevel = "INFO" 
        Job.Runner.startToil(Job.wrapJobFn(DownloadData), options) 
#	Job.Runner.startToil(Job.wrapJobFn(MerylProcess, "correct"), options)


