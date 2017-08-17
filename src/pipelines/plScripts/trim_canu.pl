
if (setOptions($mode, "trim") eq "trim") {
    if (sequenceFileExists("$asm.trimmedReads") eq undef) {
        print STDERR "--\n";
        print STDERR "--\n";
        print STDERR "-- BEGIN TRIMMING\n";
        print STDERR "--\n";

        gatekeeper($asm, "obt", @inputFiles);

        merylConfigure($asm, "obt");
        merylCheck($asm, "obt")  foreach (1..getGlobal("canuIterationMax") + 1);
        merylProcess($asm, "obt");

        overlap($asm, "obt");

        trimReads ($asm);
        splitReads($asm);
        dumpReads ($asm);
        #summarizeReads($asm);

        buildHTML($asm, "obt");
    }

    my $trimmedReads = sequenceFileExists("$asm.trimmedReads");

    caExit("can't find trimmed reads '$asm.trimmedReads*' in directory '" . getcwd() . "'", undef)  if (!defined($trimmedReads));

    undef @inputFiles;
    push  @inputFiles, "-$type-corrected\0$trimmedReads";
}

