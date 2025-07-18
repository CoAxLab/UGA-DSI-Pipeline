import os

pipelineDirectory = os.getcwd()
niftiDirectory = os.path.join(pipelineDirectory, 'convertToBids')
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')
lowBFiles = os.path.join(pipelineDirectory, 'lowBFiles')
setup = False
try:
    os.mkdir(parentBIDS)
    os.mkdir(lowBFiles)
    setup = True
except Exception as e:
    print(f'\nmoving on without additional setup steps...\n')
descFName = 'dataset_description.json'
if setup:
    os.system(f'cp CHANGEME_dataset_description.json {os.path.join(parentBIDS, descFName)}')
    os.chdir(parentBIDS)
    #os.system('touch dataset_description.json')
    os.system('touch participants.tsv')
    os.chdir(pipelineDirectory)

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

allSubIDs = []

for subjID in os.listdir(niftiDirectory):
    allSubIDs.append(subjID)
    currSubDir = os.path.join(niftiDirectory, subjID)
    outDirectory = os.path.join(parentBIDS, f'sub-{subjID}')
    outTempDir = os.path.join(lowBFiles, f'sub-{subjID}')
    try:
        os.mkdir(outDirectory)
    except Exception as e:
        print(f'{e}\nMoving on from participant {subjID}...')
        continue
    os.mkdir(outTempDir)
    print(outTempDir)

    sesN = 1
    for sesID in os.listdir(currSubDir):
        currNifti = os.path.join(currSubDir, sesID)
        sesOutDir = os.path.join(outDirectory, f'ses-{sesN}')
        sesOutTempDir = os.path.join(outTempDir, f'ses-{sesN}')
        os.mkdir(sesOutDir)
        os.mkdir(sesOutTempDir)

        anatDir = os.path.join(sesOutDir, 'anat')
        dwiDir = os.path.join(sesOutDir, 'dwi')
        dwiTempDir = os.path.join(sesOutTempDir, 'dwi')
        os.mkdir(anatDir)
        os.mkdir(dwiDir)
        os.mkdir(dwiTempDir)
        
        #print(os.listdir(currNifti))
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
                print(f'****PIPELINE: No destination for {fileToMove}, doing nothing, and moving on...')
                continue

            '''
            change the content of the below statement between passs and continue based on desire for b10 files in output
            '''
            if 'b10_' in fileToMove:
                #continue
                toHere = os.path.join(dwiTempDir, newFile)
                pass
            '''
            '''

            copyCMD = f'cp {oldFile} {toHere}'
            #print(copyCMD)
            os.system(copyCMD)
        sesN += 1