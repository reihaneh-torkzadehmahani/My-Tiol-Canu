#!/usr/bin/env perl

use strict;
use warnings;

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

#  Initialize our defaults.  Must be done before defaults are reported in printOptions() below.


#  The bin directory is needed for -version, can only be set after setDefaults(), but really should be
#  set after checkParameters() so it can know pathMap.

my $cmd     = undef;              #  Temporary string passed to system().
my $asm     = undef;              #  Name of our assembly.
my $mode=undef; 
my $filename="/tmp/MC1Parameters.txt";

$mode="run";
$asm="ecoli";

chdir('./ecoil-oxford2');

$ENV{'CANU_DIRECTORY'} = getcwd();


restoreParameters();

#------------------------------------------------------------------------------------
my $Step = $ARGV[0];
my $merylPath=$ARGV[1];
if ($Step eq "correct"){       
	#foreach (1..getGlobal("canuIterationMax") + 1){
    	foreach (1..3){
		merylCheck2($asm, "cor",$merylPath );
        }

}elsif ($Step eq "trim"){
#	foreach (1..getGlobal("canuIterationMax") + 1){
#                merylCheck1($asm, "obt");
	foreach (1..3){ 
               merylCheck2($asm, "obt", $merylPath);
	}
}elsif ($Step eq "assemble"){
#	foreach (1..getGlobal("canuIterationMax") + 1){
#                merylCheck1($asm, "utg");
	foreach (1..3){
                merylCheck2($asm, "utg", $merylPath);
	}
}else{
die "Step is not valid!!! \n"; }

#------------------------------------------------------------------------------------

saveParameters();


