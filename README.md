## Canu

Canu is a fork of the [Celera Assembler](http://wgs-assembler.sourceforge.net/wiki/index.php?title=Main_Page), designed for high-noise single-molecule sequencing (such as the [PacBio](http://www.pacb.com) [RS II](http://www.pacb.com/products-and-services/pacbio-systems/rsii/)/[Sequel](http://www.pacb.com/products-and-services/pacbio-systems/sequel/) or [Oxford Nanopore](https://www.nanoporetech.com/) [MinION](https://nanoporetech.com/products)).

Canu is a hierarchical assembly pipeline which runs in four steps:

* Detect overlaps in high-noise sequences using [MHAP](https://github.com/marbl/MHAP)
* Generate corrected sequence consensus
* Trim corrected sequences
* Assemble trimmed corrected sequences

## Citation:
 - Koren S, Walenz BP, Berlin K, Miller JR, Phillippy AM. [Canu: scalable and accurate long-read assembly via adaptive k-mer weighting and repeat separation](https://doi.org/10.1101/gr.215087.116). Genome Research. (2017).
 
 ## How to run My-Toil-Canu:
 
        git clone https://github.com/reihaneh-torkzadehmahani/canu.git
        sudo chmod 755 ./canu/RunScript.sh
        cd canu
        ./RunScript.sh
      
        cd Linux-amd64/bin/
        python ToilCanu.py -c """/home/ubuntu/canu/Linux-amd64/bin/""" -o '-p ecoli -d ecoil-oxford2 genomeSize=4.8m corMinCoverage=0 corMaxEvidenceErate=0.22 "corMhapOptions=--threshold 0.8 --num-hashes 512 --ordered-sketch-size 1000 --ordered-kmer-size 14"  -nanopore-raw oxford.fasta'

 
 
