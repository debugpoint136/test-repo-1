NCBI-BLAST Common URL API allows you run BLAST searches remotely via a REST API.

All requests to the API must include `CMD` parameter which can take one of four arguments:
- `Put` - for submitting searches
- `Get` - for checking the status of submission or retrieving results
- `Delete` - to remove a search and its results
- `DisplayRIDs` - to list all RIDs in the system

Parameters:

* PUT - `QUERY` - search query as Accession, GI or FASTA sequence
* PUT - `DATABASE` - specify BLAST database or a database uploaded to blastdb_custom
* PUT - `PROGRAM` - specify the BLAST program to use: blastn, megablast, blastp, blastx, tblastn, tblastx
* PUT - `FILTER` - specify low complexity filtering: `F` to disable; `T` or `L` to enable
* PUT/GET - `FORMAT_TYPE` - specify report type: HTML, Text, XML, XML2, JSON2, Tabular
* PUT - `EXPECT` - specify the e-value cutoff
* PUT - `MATRIX` - specify scoring matrix name: BLOSUM45, BLOSUM50, BLOSUM62, BLOSUM80, BLOSUM90, PAM250, PAM30, PAM70. Default: BLOSUM62
* PUT/GET - `HITLIST_SIZE` - specify the number of databases sequences to keep
* PUT/GET - `DESCRIPTIONS` - number of descriptions to print (applicable to HTML and Text `FORMAT_TYPE`)
* PUT/GET - `ALIGNMENTS` - number of alignments to print (applicable to HTML and Text `FORMAT_TYPE`)
* PUT/GET - `NCBI_GI` - specify whether to show NCBI GI in report: `T` or `F`
* GET/DELETE - `RID` - BLAST search request
* GET - `FORMAT_OBJECT` - `SearchInfo` for status check or `Alignment` for report formatting
* PUT - `NUM_THREADS` - specify number of virtual CPUs to use. Supported only on BlastCloud.


More details available at [NCBI GitHub](https://ncbi.github.io/blast-cloud/dev/api.html).

### BlastCloud

NCBI provides a BLAST server image to be hosted with AWS or GCE.
This allows users to run a stand-alone searches with the BLAST+ applications.
The server image includes a FUSE client that will downloda BLAST databases during the first search.
Ther server image runs on Ubuntu Linux.


### Stages of BLAST web services:

#### 1. Send Query
```
curl "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&DATABASE=nr&QUERY=TAGCTAGCATCGATCATCATCGATCAGCATCATTAGCATCGACTATCGCGCGCTACTACTAGCTAGCACTG"
```

The server will respond with HTML containing a `QBlastInfo` block. The `QBlastInfo` block will contain a RID ("Request ID") that can be used to retrieve results as well as a RTOE that is an estimated time in seconds until the search is completed. 

An example QBlastInfo block is:
```
<!--QBlastInfoBegin
   RID = SYZDXEWK014  
   RTOE = 31  
QBlastInfoEnd
-->
```

#### 2. Poll for progress and status
```
curl "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_OBJECT=SearchInfo&RID=T3PBWG67014"
```
where `T3PBWG67014` is your job id

#### 3. Fetch results upon completion
```
curl "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID=T3PBWG67014"
```
where `T3PBWG67014` is your job id
