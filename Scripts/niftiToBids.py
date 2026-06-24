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
        if 'x_' in file:
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

def DoDicomToNifti(input = dicomDirectory)->None:
    try:
        os.mkdir(niftiDirectory)
    except Exception as e:
        Debug.Log(f'{e}')
    for sub in os.listdir(input):
        pathToDcm = os.pat.join(input, sub)
        outPath = os.path.join(niftiDirectory, sub)
        ## Make this correct................................................................................
        dcmCommand = f'dcm2niix --input={pathToDcm} --output={outPath}'
        os.system(dcmCommand)

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
        outDirectory = os.path.join(parentBIDS, f'sub-{subjID}')

        skip = False

        try:
            os.mkdir(outDirectory)
        except Exception as e:
            Debug.Log(f'BIDS output directories (at Data/AnalysisData/) already exist for {subjID}.\nMoving on...', DEBUG)
            skip = True
        if skip == True:
            continue

        sesN = 1
        for sesID in os.listdir(currSubDir):
            currNifti = os.path.join(currSubDir, sesID)
            sesOutDir = os.path.join(outDirectory, f'ses-{sesN}')
            os.mkdir(sesOutDir)

            anatDir = os.path.join(sesOutDir, 'anat')
            dwiDir = os.path.join(sesOutDir, 'dwi')
            os.mkdir(anatDir)
            os.mkdir(dwiDir)
            
            for fileToMove in os.listdir(currNifti):
                # Begin sorting files from nifti directory
                oldFile = os.path.join(currNifti, fileToMove)
                subSesTag = f'sub-{subjID}_ses-{sesN}'
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
            sesN += 1


def main()->None:
    NiftiToBIDS()

if __name__ == "__main__":
    main()