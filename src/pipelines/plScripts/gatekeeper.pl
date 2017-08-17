#!/usr/bin/env perl

use strict;

use FindBin;
use Cwd qw(getcwd abs_path);

use lib "$FindBin::RealBin/lib";
use lib "$FindBin::RealBin/lib/canu/lib/perl5";
use lib "$FindBin::RealBin/lib/canu/lib64/perl5";

use File::Path 2.08 qw(make_path remove_tree);

use Carp;

use canu::Defaults;
use canu::Execution;

use canu::Configure;

use canu::Grid;
use canu::Grid_Cloud;
use canu::Grid_SGE;
use canu::Grid_Slurm;
use canu::Grid_PBSTorque;
use canu::Grid_LSF;
use canu::Grid_DNANexus;

use canu::Gatekeeper;
use canu::Meryl;
use canu::OverlapInCore;
use canu::OverlapMhap;
use canu::OverlapMMap;
use canu::OverlapStore;

use canu::CorrectReads;
use canu::ErrorEstimate;

use canu::OverlapBasedTrimming;

use canu::OverlapErrorAdjustment;
use canu::Unitig;
use canu::Consensus;
use canu::Output;

use canu::HTML;

# ----------------------------------------------------------------------------------------------

my @inputFiles;
my $cmd     = undef;              #  Temporary string passed to system().
my $asm     = undef;              #  Name of our assembly.
my $mode=undef; 
my $type= undef;
my @specOpts;
my $rootdir;
my $bin;

$mode="run";
$asm="ecoli";
$type= "nanopore";
@inputFiles="-nanopore-raw/home/ubuntu/canu/Linux-amd64/bin/oxford.fasta";
@specOpts=("genomeSize=4.8m", "corMinCoverage=0", "corMaxEvidenceErate=0.22", "errorRate=0.045", "corMhapOptions=--threshold 0.8 --num-hashes 512 --ordered-sketch-size 1000 --ordered-kmer-size 14");
$rootdir= "ecoil-oxford2";

chdir('./ecoil-oxford2');

# -------------------------------------------- set Options ---------------------------------------
sub setOptions ($$) {
    my $mode = shift @_;  #  E.g,. "run" or "trim-assemble" or just plain ol' "trim"
    my $step = shift @_;  #  Step we're setting options for.

    #  Decide if we care about running this step in this mode.  I almost applied
    #  De Morgan's Laws to this.  I don't think it would have been any clearer.

    if (($mode eq $step) ||
        ($mode eq "run") ||
        (($mode eq "trim-assemble") && ($step eq "trim")) ||
        (($mode eq "trim-assemble") && ($step eq "assemble"))) {
        #  Do run this.
    } else {
        return("don't run this");
    }

    #  Create directories for the step, if needed.

    make_path("correction")  if ((! -d "correction") && ($step eq "correct"));
    make_path("trimming")    if ((! -d "trimming")   && ($step eq "trim"));
    make_path("unitigging")  if ((! -d "unitigging") && ($step eq "assemble"));

    #  Return that we want to run this step.

    return($step);
}
#-------------------------------------------------------------------------------------------------
restoreParameters();

#-------------------------------------------------------------------------------------------------
my $step = $ARGV[0]; 
if ($step eq "trim"){
my $correctedReads = sequenceFileExists("$asm.correctedReads");

    caExit("can't find corrected reads '$asm.correctedReads*' in directory '" . getcwd() . "'", undef)  if (!defined($correctedReads));

    undef @inputFiles;
    push  @inputFiles, "-$type-corrected\0$correctedReads";
#--------------------------

if (setOptions($mode, "trim") eq "trim") {
    if (sequenceFileExists("$asm.trimmedReads") eq undef) {
        print STDERR "--\n";
        print STDERR "--\n";
        print STDERR "-- BEGIN TRIMMING\n";
        print STDERR "--\n";
      
gatekeeper($asm, "obt", @inputFiles);
}
}
#-------------------------------------------------------------------------------------------------
}elsif ($step eq "assemble"){
my $trimmedReads = sequenceFileExists("$asm.trimmedReads");

    caExit("can't find trimmed reads '$asm.trimmedReads*' in directory '" . getcwd() . "'", undef)  if (!defined($trimmedReads));

    undef @inputFiles;
    push  @inputFiles, "-$type-corrected\0$trimmedReads";
#--------------------------
if (setOptions($mode, "assemble") eq "assemble") {
    if (sequenceFileExists("$asm.contigs") eq undef) {
        print STDERR "--\n";
        print STDERR "--\n";
        print STDERR "-- BEGIN ASSEMBLY\n";
        print STDERR "--\n";

        gatekeeper($asm, "utg", @inputFiles);
}
}
}else{
die "Step is not valid!!! \n";}
#-------------------------------------------------------------------------------------------------

saveParameters();


