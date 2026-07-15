import os
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()
dicomDirectory = os.path.join(pipelineDirectory, 'Data', 'DICOM')
niftiDirectory = os.path.join(pipelineDirectory, 'Data', 'InputData')
parentBIDS = os.path.join(pipelineDirectory, 'Data', 'AnalysisData')

DEBUG = False

def getFileName(file, sub):
    '''returns (newFilename, destination)'''
    newName = f'{sub}'

    # ignore unneeded
    skipThese = ['ORIG', 'Calibration', '.mat', '.txt']
    for bad in skipThese:
        if bad in file:
            return None, None
        
    if 'hyper3' in file:
        # file is for dwi
        dest = 'dwi'
        # add dir tag
        if 'x_' in file or '!' in file:
            newName = f'{newName}_dir-rev' 
        else:
            newName = f'{newName}_dir-std' 
        
        # add acq tag
        if 'b2000_' in file:
            newName = f'{newName}_acq-midb_dwi' 
        elif 'b10_' in file:
            newName = f'{newName}_acq-lowb_dwi'
        elif 'b4000_' in file:
            newName = f'{newName}_acq-highb_dwi'

        # add file ext
        if '.nii.gz' in file:
            newName = f'{newName}.nii.gz'
        elif '.bval' in file:
            newName = f'{newName}.bval'
        elif '.bvec' in file:
            newName = f'{newName}.bvec'

    else:
        # file is for anat
        dest = 'anat'
        if 'T2' in file:
            if 'FLAIR' in file:
                newName = f'{newName}_acq-flair'
            elif 'CUBE' in file:
                newName = f'{newName}_acq-cube'
            newName = f'{newName}_T2w.nii.gz'
        else:
            if 'T1' in file:
                newName = f'{newName}_T1w.nii.gz'
    if '.' in newName: return newName, dest
    else: return None, None

def DoDicomToNifti(sesPath:str)->None:
    '''
    Run dcm2niix on DICOM folder.
    Read nifti output JSON to rename newly created files.
    '''

    dcmCommand = f'dcm2niix -z y -b y -f "%d" {sesPath}'
    os.system(dcmCommand)

    # for file in os.listdir(sesPath):
        
    #     filePath = os.path.join(sesPath, file)

    #     if os.path.isdir(filePath):
    #         Debug.Log(f'Searching for JSON... Skipping {file}...')
    #         continue

        
    #     baseName = file.replace('.json', '')

    #     try:
    #         with open(jsonPath, "r") as f:
    #             scanData = json.load(f)
    #     except (json.JSONDecodeError, OSError) as e:
    #         Debug.Log(f"Skipping '{baseName}': could not read/parse JSON ({e})")
    #         continue

    #     if "SeriesDescription" not in scanData:
    #             Debug.Log(f"Skipping '{baseName}': key 'SeriesDescription' not found in JSON")
    #             continue
    #     newName = str(scanData["SeriesDescription"]).strip()
    #     if not newName:
    #         print(f"Skipping '{baseName}': 'SeriesDescription' value is empty")
    #         continue

def NiftiToBIDS(inputDir:str = None)->None:
    setup = False
    if inputDir == None:
        inputDir = niftiDirectory
    try:
        os.mkdir(parentBIDS)
        setup = True
    except Exception as e:
        pass # Further setup is not needed.

    descFName = 'dataset_description.json'
    if setup:
        os.system(f'cp CHANGEME_dataset_description.json {os.path.join(parentBIDS, descFName)}')
        os.chdir(parentBIDS)
        os.system('touch participants.tsv')
        os.chdir(pipelineDirectory)

    allSubIDs = []

    for subjID in os.listdir(inputDir):
        allSubIDs.append(subjID)
        currSubDir = os.path.join(inputDir, subjID)

        if 'sub-' in subjID:
            addSubTag = f''
        else:
            addSubTag = f'sub-'

        outDirectory = os.path.join(parentBIDS, f'{addSubTag}{subjID}')

        skip = False

        try:
            os.mkdir(outDirectory)
        except Exception as e:
            Debug.Log(f'BIDS output directories (at Data/AnalysisData/) already exist for {subjID}.\nMoving on...', DEBUG)
            skip = True
        if skip == True:
            continue

        #sesN = 1
        for sesID in os.listdir(currSubDir):
            currNifti = os.path.join(currSubDir, sesID)
            sessionTag = sesID
            if 'ses-' not in sessionTag:
                sessionTag = f'ses-{sessionTag}'
            sesOutDir = os.path.join(outDirectory, sessionTag)
            os.mkdir(sesOutDir)

            anatDir = os.path.join(sesOutDir, 'anat')
            dwiDir = os.path.join(sesOutDir, 'dwi')
            os.mkdir(anatDir)
            os.mkdir(dwiDir)

            foundFile = False
            for content in os.listdir(currNifti):
                if not os.path.isdir(os.path.join(currNifti, content)):
                    foundFile = True
                    break

            if foundFile == False:
                DoDicomToNifti(currNifti)
            
            for fileToMove in os.listdir(currNifti):
                # Begin sorting files from nifti directory
                oldFile = os.path.join(currNifti, fileToMove)
                if os.path.isdir(oldFile):
                    continue # skip DICOM directories if they exist
                subSesTag = f'{addSubTag}{subjID}_{sessionTag}'
                newFile, destination = getFileName(fileToMove, subSesTag)
                if destination == 'anat':
                    toHere = os.path.join(anatDir, newFile)
                elif destination == 'dwi':
                    toHere = os.path.join(dwiDir, newFile)
                elif destination == None:
                    Debug.Log(f'****PIPELINE: No destination for {fileToMove}, doing nothing, and moving on...')
                    continue

                '''
                change the content of the below statement between passs and continue based on desire for b10 files in output
                '''

                if 'flair' in fileToMove:
                    continue
                '''
                Do not move T2w flair data
                '''

                copyCMD = f'cp {oldFile} {toHere}'

                os.system(copyCMD)
            #sesN += 1


def main()->None:
    NiftiToBIDS()

if __name__ == "__main__":
    main()