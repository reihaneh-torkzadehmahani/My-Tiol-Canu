    caExit("can't find corrected reads '$asm.correctedReads*' in directory '" . getcwd() . "'", undef)  if (!defined($correctedReads));

    undef @inputFiles;
    push  @inputFiles, "-$type-corrected\0$correctedReads";
}
