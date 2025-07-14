# DSI Singularity Pipeline
<br/>
Must have Singularity and its dependencies installed locally.
<br/>
https://docs.sylabs.io/guides/latest/user-guide/quick_start.html
<br/>
Run the one-time setup script to initialize directories and SIF file.
<br/>
<br/>
-- runQC.py runs MRIQC sequentially on each subject's T1w and T2w scans, one session at a time. If a session output folder exists (ex. sub-01/ses-X/) already, subject 01's session X will be skipped.
<br/>
-- runPipeline.py runs DSI Studio's 'src' action sequentially for each subject's diffusion scans. The outputs from this process are used in the 'rec' action process which is executed immediately following the completion of the final subject's src action. For both src and rec, if an output folder exists for a subject/session combination, this combination will be skipped.
<br/>
***I an output folder exixts, and the process it prevents must be re-run, or run without crashing, simply delete the problematic OUTPUT folder.***