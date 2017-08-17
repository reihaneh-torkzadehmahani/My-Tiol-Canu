
if (setOptions($mode, "assemble") eq "assemble") {
    if (sequenceFileExists("$asm.contigs") eq undef) {
        print STDERR "--\n";
        print STDERR "--\n";
        print STDERR "-- BEGIN ASSEMBLY\n";
        print STDERR "--\n";

        gatekeeper($asm, "utg", @inputFiles);

        merylConfigure($asm, "utg");
        merylCheck($asm, "utg")  foreach (1..getGlobal("canuIterationMax") + 1);
        merylProcess($asm, "utg");

        overlap($asm, "utg");

        #readErrorDetection($asm);

        readErrorDetectionConfigure($asm);
        readErrorDetectionCheck($asm)  foreach (1..getGlobal("canuIterationMax") + 1);

        overlapErrorAdjustmentConfigure($asm);
        overlapErrorAdjustmentCheck($asm)  foreach (1..getGlobal("canuIterationMax") + 1);

        updateOverlapStore($asm);

        unitig($asm);
        unitigCheck($asm)  foreach (1..getGlobal("canuIterationMax") + 1);

        foreach (1..getGlobal("canuIterationMax") + 1) {   #  Consensus wants to change the script between the first and
            consensusConfigure($asm);                      #  second iterations.  The script is rewritten in
            consensusCheck($asm);                          #  consensusConfigure(), so we need to add that to the loop.
        }

        consensusLoad($asm);
        consensusAnalyze($asm);

        alignGFA($asm)  foreach (1..getGlobal("canuIterationMax") + 1);

        generateOutputs($asm);
    }
}

print STDERR "--\n";
print STDERR "-- Bye.\n";

exit(0);
