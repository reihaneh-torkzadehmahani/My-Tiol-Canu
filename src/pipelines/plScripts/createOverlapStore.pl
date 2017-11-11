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

restoreParameters();

sub createOvlStore ($$) {
    my $asm  = shift @_;
    my $tag  = shift @_;

    createOverlapStore($asm, $tag, getGlobal("ovsMethod"));
}


my $Step= $ARGV[0];

if ($Step eq "correct"){
  createOvlStore($asm, "cor");

} elsif ($Step eq "trim"){
  createOvlStore($asm, "obt");

} elsif ($Step eq "assemble"){
  createOvlStore($asm, "utg");
} else {
die "Step is not valid!!!! \n";}

saveParameters();

