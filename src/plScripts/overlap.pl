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

#  Initialize our defaults.  Must be done before defaults are reported in printOptions() below.


#  The bin directory is needed for -version, can only be set after setDefaults(), but really should be
#  set after checkParameters() so it can know pathMap.

my $cmd     = undef;              #  Temporary string passed to system().
my $asm     = undef;              #  Name of our assembly.
my $mode=undef; 

$mode="run";
$asm="ecoli";

chdir('./ecoil-oxford2');

$ENV{'CANU_DIRECTORY'} = getcwd();


sub overlap0 ($$) {
    my $asm  = shift @_;
    my $tag  = shift @_;

    my $ovlType = ($tag eq "utg") ? "normal" : "partial";

    if (getGlobal("${tag}overlapper") eq "mhap") {
        mhapConfigure($asm, $tag, $ovlType);

#        mhapPrecomputeCheck($asm, $tag, $ovlType)  foreach (1..getGlobal("canuIterationMax") + 1);
        mhapPrecomputeCheck($asm, $tag, $ovlType)  foreach (1..3);
#	mhapPrecomputeCheck($asm, $tag, $ovlType);

        #  this also does mhapReAlign

#        mhapCheck($asm, $tag, $ovlType)  foreach (1..getGlobal("canuIterationMax") + 1);

   } elsif (getGlobal("${tag}overlapper") eq "minimap") {
        mmapConfigure($asm, $tag, $ovlType);

#       mmapPrecomputeCheck($asm, $tag, $ovlType)  foreach (1..getGlobal("canuIterationMax") + 1);
        mmapPrecomputeCheck($asm, $tag, $ovlType)  foreach (1..3);
	#mmapPrecomputeCheck($asm, $tag, $ovlType);

#       mmapCheck($asm, $tag, $ovlType)   foreach (1..getGlobal("canuIterationMax") + 1);
	
    } else {
        overlapConfigure($asm, $tag, $ovlType);

#       overlapCheck($asm, $tag, $ovlType)  foreach (1..getGlobal("canuIterationMax") + 1);
	
	overlapCheck($asm, $tag, $ovlType)  foreach (1..3);

#	overlapCheck($asm, $tag, $ovlType);
    #    createOverlapStore($asm, $tag, getGlobal("ovsMethod")); 
   }

#    createOverlapStore($asm, $tag, getGlobal("ovsMethod"));
}
#############################################################################################################
sub overlap1 ($$) {
    my $asm  = shift @_;
    my $tag  = shift @_;

    my $ovlType = ($tag eq "utg") ? "normal" : "partial";

    if (getGlobal("${tag}overlapper") eq "mhap") {
        #  this also does mhapReAlign
#        mhapCheck($asm, $tag, $ovlType)  foreach (1..getGlobal("canuIterationMax") + 1);
         mhapCheck($asm, $tag, $ovlType)  foreach (1..3);
#        mhapCheck($asm, $tag, $ovlType);

   } elsif (getGlobal("${tag}overlapper") eq "minimap") {
#       mmapCheck($asm, $tag, $ovlType)   foreach (1..getGlobal("canuIterationMax") + 1);
	mmapCheck($asm, $tag, $ovlType)   foreach (1..3);
#        mmapCheck($asm, $tag, $ovlType);
    }
createOverlapStore($asm, $tag, getGlobal("ovsMethod")); 
}

#-------------------------------------------------------------------------------------------------------------
restoreParameters();

#-------------------------------------------------------------------------------------------------------------        
my $Step= $ARGV[0];

if ($Step eq "correct0"){
overlap0($asm, "cor");

}elsif ($Step eq "trim0"){
overlap0($asm, "obt");

}elsif ($Step eq "assemble0"){
overlap0($asm, "utg");

}elsif ($Step eq "correct1"){
overlap1($asm, "cor");

}elsif ($Step eq "trim1"){
overlap1($asm, "obt");

}elsif ($Step eq "assemble1"){
overlap1($asm, "utg");

} else {
die "Step is not valid!!!! \n";}
#-------------------------------------------------------------------------------------------------------------

saveParameters();
