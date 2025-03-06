import os

pipelineDirectory = os.getcwd()
niftiDirectory = os.path.join(pipelineDirectory, 'convertToBids')
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')
setup = False
try:
    os.mkdir(parentBIDS)
    setup = True
except Exception as e:
    print(f'\nmoving on...\n')
if setup:
    os.chdir(parentBIDS)
    os.system('touch dataset_description.json')
    os.system('touch participants.tsv')
    os.chdir(pipelineDirectory)

def getFileName(file, sub):
    '''returns (newFilename, destination)'''
    newName = f'sub-{sub}'

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



for subjID in os.listdir(niftiDirectory):
    outDirectory = os.path.join(parentBIDS, f'sub-{subjID}')
    currNifti = os.path.join(niftiDirectory, subjID)
    anatDir = os.path.join(outDirectory, 'anat')
    dwiDir = os.path.join(outDirectory, 'dwi')
    try:
        os.mkdir(outDirectory)
    except Exception as e:
        print(f'{e}\nMoving on from participant {subjID}...')
        continue
    os.mkdir(anatDir)
    os.mkdir(dwiDir)
    
    print(os.listdir(currNifti))
    for fileToMove in os.listdir(currNifti):
        '''change the content of the below statement between passs and continue based on desire for b10 files in output'''
        if 'lowb' in fileToMove:
            continue
            #pass
        # Begin sorting files from nifti directory
        oldFile = os.path.join(currNifti, fileToMove)
        newFile, destination = getFileName(fileToMove, subjID)
        match destination:
            case 'anat':
                toHere = os.path.join(anatDir, newFile)
            case 'dwi':
                toHere = os.path.join(dwiDir, newFile)
            case None:
                continue
        copyCMD = f'cp {oldFile} {toHere}'
        print(copyCMD)
        os.system(copyCMD)