
if (setOptions($mode, "correct") eq "correct") {
    if (sequenceFileExists("$asm.correctedReads") eq undef) {
        print STDERR "--\n";
        print STDERR "--\n";
        print STDERR "-- BEGIN CORRECTION\n";
        print STDERR "--\n";
          
        printGlobal();
        gatekeeper($asm, "cor", @inputFiles);
        printGlobal();
        merylConfigure($asm, "cor");
        merylCheck($asm, "cor")  foreach (1..getGlobal("canuIterationMax") + 1);
        merylProcess($asm, "cor");

        overlap($asm, "cor");

        buildCorrectionLayouts($asm);
        generateCorrectedReads($asm)  foreach (1..getGlobal("canuIterationMax") + 1);
        dumpCorrectedReads($asm);

        buildHTML($asm, "cor");
    }

    my $correctedReads = sequenceFileExists("$asm.correctedReads");

    caExit("can't find corrected reads '$asm.correctedReads*' in directory '" . getcwd() . "'", undef)  if (!defined($correctedReads));

    undef @inputFiles;
    push  @inputFiles, "-$type-corrected\0$correctedReads";
}

