import sys, getopt
from toil.job import Job
from toil.common import Toil
import os
import subprocess
import sh
import urllib

CanuBinDir = ''
CanuOptions = ''

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
def DownloadData(job):
    os.chdir(CanuBinDir)
#    url = "http://nanopore.s3.climb.ac.uk/MAP006-PCR-1_2D_pass.fasta"
    fileName=os.path.join(CanuBinDir, 'oxford.fasta')
    fileName=CanuBinDir+'/oxford.fasta'
#    urllib.urlretrieve(url, fileName)
    job.fileStore.logToMaster("Data has been downloaded successfully!")
    CS = Job.wrapJobFn(CanuStart)
    job.addFollowOn(CS)
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
        os.chdir(CanuBinDir)
#open file and read parameters (path + merylPath)
	content1=0
	p=0
	if (step == "correct"):
		
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

	
        elif (step == "trim"):
                cmd = './merylCheck1.pl trim'
       		os.system(cmd)
	elif (step =="assemble"):
                cmd = './merylCheck1.pl assemble'
        	os.system(cmd)
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
        os.chdir(CanuBinDir)
        tCount= len (PScripts)-1
        if (step == "correct"):
                if (fn=="MerylCheck"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/0-mercounts/'
               		os.chdir(currentDir)
		elif (fn == "Overlap0" or fn=="Overlap1"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/1-overlapper/'
			os.chdir(currentDir)
                elif (fn== "GenerateCorrectedReads"):
                        currentDir= CanuBinDir + 'ecoil-oxford2/correction'+ '/2-correction/'
			os.chdir(currentDir)
	if count>=0 :
                job.fileStore.logToMaster("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa %s uuuuuuuuuuu  %s" %(fn , step))
		command=  PScripts[(tCount-count)]
                #command=command.replace ("./", currentDir)
		#command="/home/ubuntu/canu/Linux-amd64/bin/ecoil-oxford2/correction/0-mercounts/meryl.sh 1 > /home/ubuntu/canu/Linux-amd64/bin/ecoil-oxford2/correction/0-mercounts/meryl.000001.out 2>&1"
		os.system(command)
		job.fileStore.logToMaster("****************COMMAND*************" + command )
		#subprocess.call(['ls', '-lh'])
                job.fileStore.logToMaster("Job has been submitted!! "+ "( "  ")" )
                RS = Job.wrapJobFn(RunScripts,PScripts, count-1, step, fn)
                job.addChild(RS)
        else:
                job.fileStore.logToMaster("RunScripts job is DONE! " )

                if (fn =="MerylCheck"):
                        MP = Job.wrapJobFn(MerylProcess, step)
                        job.addFollowOn(MP)
                elif (fn == "Overlap0"):
                        Ov1=Job.wrapJobFn(Overlap1, step)
                        job.addFollowOn(Ov1)

                elif (fn == "Overlap1"):
                        Bcl=Job.wrapJobFn(BuildCorrectionLayouts)
                        job.addFollowOn(Bcl)
                elif (fn== "GenerateCorrectedReads"):
                        Dcr = Job.wrapJobFn(DumpCorrectedReads)
                        job.addFollowOn(Dcr)
#-----------------------------------------------------------------------------------------------#
def MerylProcess(job, step):
        os.chdir(CanuBinDir)

	if (step == "correct"):
                cmd = './merylProcess.pl correct'
        elif (step == "trim"):
                cmd = './merylProcess.pl trim'
        elif (step =="assemble"):
                cmd = './merylProcess.pl assemble'

        os.system(cmd)
        job.fileStore.logToMaster("MeryProcess job is DONE! "+ "( "+ step + ")")
        Ov = Job.wrapJobFn(Overlap0, step)
        job.addFollowOn(Ov)
# -----------------------------------------------------------------------------------------------#  
def Overlap0(job, step):
        os.chdir(CanuBinDir)

	if (step == "correct"):
                cmd = './overlap.pl correct0'
		os.system(cmd)
		f1=open("/tmp/ProcessQueue.txt", "r")
		content1=f1.read().splitlines()
                p= len (content1)-1
        elif (step == "trim"):
                cmd = './overlap.pl trim0'
		os.system(cmd)
		T=Job.wrapJobFn(TrimReads)
                job.addFollowOn(T)

        elif (step =="assemble"):
                cmd = './overlap.pl assemble0'
		os.system(cmd)
        	R=Job.wrapJobFn(ReadErrorDetectionConfigure)
                job.addFollowOn(R)

        job.fileStore.logToMaster("Overlap0 job is DONE! "+ "( "+ step + ")")
        RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap0" )
        job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------#
def Overlap1(job, step):
        os.chdir(CanuBinDir)

        if (step == "correct"):
                cmd = './overlap.pl correct1'
                os.system(cmd)
                f1=open("/tmp/ProcessQueue.txt", "r")
                content1=f1.read().splitlines()
                p= len (content1)-1

        elif (step == "trim"):
                cmd = './overlap.pl trim1'
                os.system(cmd)
                T=Job.wrapJobFn(TrimReads)
                job.addFollowOn(T)

        elif (step =="assemble"):
                cmd = './overlap.pl assemble1'
                os.system(cmd)
                R=Job.wrapJobFn(ReadErrorDetectionConfigure)
                job.addFollowOn(R)

        job.fileStore.logToMaster("Overlap1 job is DONE! "+ "( "+ step + ")")
        RS = Job.wrapJobFn(RunScripts, content1, p, step, "Overlap1" )
        job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------# 
def BuildCorrectionLayouts(job):
        os.chdir(CanuBinDir)
        cmd = './buildCorrectionLayouts.pl'
        os.system(cmd)
        job.fileStore.logToMaster("BuildCorrectionLayouts job is DONE! ")
        Gcr = Job.wrapJobFn(GenerateCorrectedReads)
        job.addFollowOn(Gcr)
# -----------------------------------------------------------------------------------------------# 
def GenerateCorrectedReads(job):
        os.chdir(CanuBinDir)
        cmd = './generateCorrectedReads.pl'
        os.system(cmd)
	f1=open("/tmp/ProcessQueue.txt", "r")
        content1=f1.read().splitlines()
        p= len (content1)-1
        job.fileStore.logToMaster("GenerateCorrectedReads job is DONE! ")
	
	RS = Job.wrapJobFn(RunScripts, content1, p, "correct", "GenerateCorrectedReads" )
        job.addFollowOn(RS)
# -----------------------------------------------------------------------------------------------# 
def DumpCorrectedReads(job):
        os.chdir(CanuBinDir)
        cmd = './dumpCorrectedReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("DumpCorrectedReads job is DONE! ")
        BH = Job.wrapJobFn(BuildHTML, "correct")
        job.addFollowOn(BH)
# -----------------------------------------------------------------------------------------------# 
def BuildHTML(job, step):
        os.chdir(CanuBinDir)
	if (step == "correct"):
                cmd = './buildHTML.pl correct'
		os.system(cmd)
#	 	G= Job.wrapJobFn(Gatekeeper, "trim")
#        	job.addFollowOn(G)

        elif (step == "trim"):
                cmd = './buildHTML.pl trim'
		os.system(cmd)
		G = Job.wrapJobFn(Gatekeeper, "assemble")
        	job.addFollowOn(G)

        job.fileStore.logToMaster("BuildHTML job is DONE! hahahahahah "+ "( "+ step + ")")
# -----------------------------------------------------------------------------------------------# 
# -----------------------------------------------------------------------------------------------#  
def Gatekeeper (job, step):
        os.chdir(CanuBinDir)

	if (step == "trim"):
        	cmd = './gatekeeper.pl trim'
		os.system(cmd)
	elif (step =="assemble"):
		cmd = './gatekeeper.pl assemble'

        os.system(cmd)
        job.fileStore.logToMaster("Gatekeeper job is DONE! " + "( "+ step + ")" )
        MCh = Job.wrapJobFn(MerylConfigure, step)
        job.addFollowOn(MCh)
        #executeJob(job,'./merylConfigure.pl correct',"MerylConfigure","MerylCheck")
#-------------------------------------------------------------------------------------------------# 
def TrimReads(job):
        os.chdir(CanuBinDir)
        cmd = './trimReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("TrimReads job is DONE! ")
        S = Job.wrapJobFn(SplitReads)
        job.addFollowOn(S)
# -----------------------------------------------------------------------------------------------# 
def SplitReads(job):
        os.chdir(CanuBinDir)
        cmd = './splitReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("SplitReads job is DONE! ")
        D = Job.wrapJobFn(DumpReads)
        job.addFollowOn(D)
# -----------------------------------------------------------------------------------------------#  
def DumpReads(job):
        os.chdir(CanuBinDir)
        cmd = './dumpReads.pl'
        os.system(cmd)
        job.fileStore.logToMaster("DumpReads job is DONE! ")
        B=Job.wrapJobFn(BuildHTML , "trim")
        job.addFollowOn(B)
# -----------------------------------------------------------------------------------------------# 
# -----------------------------------------------------------------------------------------------# 
def ReadErrorDetectionConfigure(job):
        os.chdir(CanuBinDir)
        cmd = './readErrorDetectionConfigure.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ReadErrorDetectionConfigure job is DONE! ")
	Re = Job.wrapJobFn(ReadErrorDetectionCheck)
        job.addFollowOn(Re)
# -----------------------------------------------------------------------------------------------# 
def ReadErrorDetectionCheck(job):
        os.chdir(CanuBinDir)
        cmd = './readErrorDetectionCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ReadErrorDetectionCheck job is DONE! ")
        Oe = Job.wrapJobFn(OverlapErrorAdjustmentConfigure)
        job.addFollowOn(Oe)
# -------------------------------------------e---------------------------------------------------# 
def OverlapErrorAdjustmentConfigure(job):
        os.chdir(CanuBinDir)
        cmd = './overlapErrorAdjustmentConfigure.pl'
        os.system(cmd)
        job.fileStore.logToMaster("OverlapErrorAdjustmentConfigure job is DONE! ")
        OeA = Job.wrapJobFn(OverlapErrorAdjustmentCheck)
        job.addFollowOn(OeA)
# -----------------------------------------------------------------------------------------------# 
def OverlapErrorAdjustmentCheck(job):
        os.chdir(CanuBinDir)
        cmd = './overlapErrorAdjustmentCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("OverlapErrorAdjustmentCheck job is DONE! ")
        Uo = Job.wrapJobFn(UpdateOverlapStore)
        job.addFollowOn(Uo)
# -----------------------------------------------------------------------------------------------# 
def UpdateOverlapStore(job):
        os.chdir(CanuBinDir)
        cmd = './updateOverlapStore.pl'
        os.system(cmd)
        job.fileStore.logToMaster("UpdateOverlapStore job is DONE! ")
        U = Job.wrapJobFn(Unitig)
        job.addFollowOn(U)
# -----------------------------------------------------------------------------------------------# 
def Unitig(job):
        os.chdir(CanuBinDir)
        cmd = './unitig.pl'
        os.system(cmd)
        job.fileStore.logToMaster("Unitig job is DONE! ")
        UC = Job.wrapJobFn(UnitigCheck)
        job.addFollowOn(UC)
# -----------------------------------------------------------------------------------------------# 
def UnitigCheck(job):
        os.chdir(CanuBinDir)
        cmd = './unitigCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("UnitigCheck job is DONE! ")
        CC = Job.wrapJobFn(ConsensusConfigureCheck )
        job.addFollowOn(CC)
# -----------------------------------------------------------------------------------------------# 
def ConsensusConfigureCheck(job):
        os.chdir(CanuBinDir)
        cmd = './consensusConfigureCheck.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusConfigureCheck job is DONE! ")
        CL = Job.wrapJobFn(ConsensusLoad )
        job.addFollowOn(CL)
# -----------------------------------------------------------------------------------------------# 
def ConsensusLoad(job):
        os.chdir(CanuBinDir)
        cmd = './consensusLoad.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusLoad job is DONE! ")
        CA = Job.wrapJobFn(ConsensusAnalyze)
        job.addFollowOn(CA)
# -----------------------------------------------------------------------------------------------# 
def ConsensusAnalyze(job):
        os.chdir(CanuBinDir)
        cmd = './consensusAnalyze.pl'
        os.system(cmd)
        job.fileStore.logToMaster("ConsensusAnalyze job is DONE! ")
        A = Job.wrapJobFn(AlignGFA)
        job.addFollowOn(A)

# -----------------------------------------------------------------------------------------------# 
def AlignGFA(job):
        os.chdir(CanuBinDir)
        cmd = './alignGFA.pl'
        os.system(cmd)
        job.fileStore.logToMaster("AlignGFA job is DONE! ")
        A = Job.wrapJobFn(GenerateOutputs)
        job.addFollowOn(A)
# -----------------------------------------------------------------------------------------------# 
def GenerateOutputs(job):
        os.chdir(CanuBinDir)
        cmd = './generateOutputs.pl'
        os.system(cmd)
        job.fileStore.logToMaster("GenerateOutputs job is DONE! ")

if __name__ == "__main__":
        options = Job.Runner.getDefaultOptions("./toilWorkflow")
        options.logLevel = "DEBUG" 
        Job.Runner.startToil(Job.wrapJobFn(getArgs,sys.argv[1:]), options) 

