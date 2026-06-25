# DSI Reconstruction and MRIQC Pipeline
Welcome, please [report any issues here!](https://github.com/CoAxLab/UGA-DSI-Pipeline/issues/new)
## Setup
Begin by cloning this repository locally to your system.
```
git clone https://github.com/CoAxLab/UGA-DSI-Pipeline
```

If you have already installed the pipeline and need to update to the latest version, run this in a terminal window instead:
```
git pull origin main
```  

Python module dependencies are listed in requirements.txt.  
Install these on your base environment individually, or by using:
```
pip install -r requirements.txt
```  

Alternatively, follow [instructions to create a virtual environment.](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)  
Must have [Docker Desktop](https://docs.docker.com/desktop/) (windows/mac) or [Docker Engine](https://docs.docker.com/engine/) (linux) installed locally.

If running the app for the first time, follow these steps:
1. Run the app.
```
python PipelineApp.py
```
2. Click the button that says "Set up directories".  
This will create all the directories needed to begin using the pipeline.
3. You should now see a directory called `Data/InputData/`.  
Copy subject NIFTI formatted data to this directory.  
Name folders of copied data according to the subject's ID. DO NOT add the "sub-" tag required by BIDS format, as this will be added automatically later.  
If a subject has one session, all data may be placed in the subject folder. If there are multiple sessions, data from each session must be placed in separate folders within the subject folder (ex. `Data/InputData/SUBJ001/RunX/`, and `Data/InputData/SUBJ001/RunY/`). The names of these folders do not matter.
Alternatively, the pipeline app will allow you to select an external input directory containing NIFTI data formatted the same way as `Data/InputData/` requires.
4. All functionality beyond this will be handled within the app. You will only need to interface with the filesystem to add new subject data.

## File Architecture
Running setup creates two top-level directories alongside the pipeline code: `Data/` (subject input and BIDS-formatted data) and `Output/` (everything produced by processing and analysis steps).

```
Data/
├── InputData/         # Raw subject NIFTI data, copied here before BIDS conversion
├── IntermediateData/  # MRIQC working directory (scratch space, safe to clear)
└── AnalysisData/      # BIDS-formatted subject data (sub-*/ses-*/anat, dwi)
Output/
├── src/               # DSI Studio src files, organized by sub-*_ses-*/
├── fib/                # DSI Studio reconstruction (.fib.gz) output, organized by sub-*_ses-*/
├── QCOutput/           # MRIQC output, loosely BIDS-formatted
└── Figures/            # QA distribution plots (.png) and metadata dataframes (.csv) used by the Visualization page
```

If you're upgrading from an older version of the pipeline that used top-level `BIDS/`, `convertToBids/`, `src/`, `fib/`, `QCOutput/`, and `Figures/` directories, the "Set up directories" button will detect these and migrate them into the `Data/` and `Output/` structure above automatically.

## Usage
### Pipeline Page
This page contains buttons that will perform various data processing and analysis functions. Clicking on a button will not execute its functionality, but it will be loaded into the "Execute" button. Information about the loaded function and its targeted subjects can be found in the section on the right side of the application window.
1. "Move nifti files to BIDS directory"  

This button will sort subject data that you have copied to the `Data/InputData/` directory into BIDS format. It then moves the data to the `Data/AnalysisData/` directory with any previously converted subjects.  

2. "Run MRIQC for anatomical data"  

This button will run MRIQC using anatomical data for all listed subjects. The output can be found in the loosely-BIDS-formatted `Output/QCOutput/` directory. Working files are kept in `Data/IntermediateData/`.

3. "Run DSI Studio src action for diffusion data"  

This button will run DSI Studio's src action for all listed subjects. This process should be fairly quick for each subject. Output is located in the `Output/src/` directory.  

4. "Run DSI Studio rec action for diffusion data"  

This button runs reconstruction for each subject using DSI Studio. Its input is subject src data, located in the `Output/src/` directory. If there were issues running src for a subject, reconstruction will not run properly. This process is time consuming, and progress can be tracked in the terminal window. Reconstruction output is located in the `Output/fib/` directory.
### Visualization Page
This page shows graphs of various quality assurance measures from scanner data. You may choose to view graphs for T1w, T2w, or dwi data. The pulldown menu below the type selection will list all available QA measures. If you wish to retrieve additional data, the figure image files and QA dataframes are located in the `Output/Figures/` directory of this repository.