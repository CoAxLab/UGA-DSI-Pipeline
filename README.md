# DSI Singularity Pipeline
Welcome, please [report any issues here!](https://github.com/CoAxLab/UGA-DSI-Pipeline/issues/new) Note, it is not recommended to use Singularity on non-Linux machines. This app is intended for use with a Linux OS.
## Setup
Python module dependencies are listed in requirements.txt.  
Install these on your base environment individually, or by using:
'''
% pip install -r requirements.txt
'''  

Alternatively, follow [instructions to create a virtual environment.](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)  
Must have [Singularity](https://docs.sylabs.io/guides/latest/user-guide/quick_start.html) and its dependencies installed locally.

If runnung the app for the first time, follow these steps:
1. Begin by cloning this repository locally to your system.
'''
% git clone https://github.com/CoAxLab/UGA-DSI-Pipeline
'''
2. Run the app.
'''
% python PipelineApp.py
'''
3. Click the button that says "Set up directories".  
This will create all the directories needed to begin using the pipeline, and will create Singularity image files for both DSI Studio and MRIQC. This may take some time.
4. You should now see a directory called convertToBids/.  
Copy subject NIFTI formatted data to this directory.  
Name folders of copied data according to the subject's ID. DO NOT add the "sub-" tag required by BIDS format, as this will be added automatically later.  
If a subject has one session, all data may be placed in the subject folder. If there are multiple sessions, data from each session must be placed in separate folders within the subject folder (ex. convertToBids/PART001/RunX/, and convertToBids/PART001/RunY/). The names of these folders do not matter.
5. All functionality beyond this will be handled within the app. You will only need to interface with the filesystem to add new subject data.
## Usage
### Pipeline Page
This page contains buttons that will perform various data processing and analysis functions. Clicking on a button will not execute its functionality, but it will be loaded into the "Execute" button. Information about the loaded function and its targeted subjects can be found in the section on the right side of the application window.
1. "Move nifti files to BIDS directory"  

This button will sort subject data that you have copied to the convertToBids/ directory into BIDS format. It then moves the data to the BIDS/ directory with any previously converted subjects.
2. "Run MRIQC for anatomical data"  

This button will run MRIQC using anatomical data for all listed subjects. The Output can be found in the loosely-BIDS-formatted QCOutput/ directory.
3. "Run DSI Studio src action for diffusion data"  

This button will run DSI Studio's src action for all listed subjects. This process should be fairly quick for each subject. Output is located in the src/ directory.
4. "Run DSI Studio rec action for diffusion data"  

This button runs reconstruction for each subject using DRI Studio. Its input is subject src data, located in the src/ directory. If there were issues running src for a subject, reconstruction will not run properly. This process is time consuming, and progress can be tracked in the terminal window. Reconstruction output is located in the fib/ directory.
### Visualization Page
This page shows graphs of various quality assurance measures from scanner data. You may choose to view graphs for T1w, T2w, or dwi data. The pulldown menu below the type selection will list all available QA measures. If you wish to retrieve additional data, the figure image files and QA dataframes are located in the Figures/ directory of this repository.
