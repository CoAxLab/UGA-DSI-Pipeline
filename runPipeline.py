import os
import time

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')

singularityCommand = f'singularity exec {sifFile}'

## run src process using b10, b2000, b4000 for each subject
for subjID in os.listdir(bidsDirectory):
    if 'sub-' not in subjID: continue
    subBidsPath = os.path.join(bidsDirectory, subjID)
    subjectSRCDir = os.path.join(outputDirectorySRC, subjID)
    try:
        os.mkdir(subjectSRCDir)
    except FileExistsError:
        print(f'\nsrc action already complete for subject: {subjID}!\n')
        continue

    for sesDir in os.listdir(subBidsPath):
        sesSRCDir = os.path.join(subjectSRCDir, sesDir)
        os.mkdir(sesSRCDir)
        # source files:
        lowStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-lowb_dwi.nii.gz')
        midStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-midb_dwi.nii.gz')
        highSandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-highb_dwi.nii.gz')
        # output file:
        stdOutFile = os.path.join(sesSRCDir, f'{subjID}_{sesDir}_dir-std.src.gz')
        srcCommandStandard = f'dsi_studio --action=src --source={lowStandard} --other_source={midStandard},{highSandard} --output={stdOutFile}'

        # reversed source files:
        lowReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-lowb_dwi.nii.gz')
        midReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-midb_dwi.nii.gz')
        highReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-highb_dwi.nii.gz')
        # reversed output file:
        revOutFile = os.path.join(sesSRCDir, f'{subjID}_{sesDir}_dir-rev.src.gz')

        srcCommandReversed = f'dsi_studio --action=src --source={lowReverse} --other_source={midReverse},{highReverse} --output={revOutFile}'

        fullCommandStandard = f'{singularityCommand} {srcCommandStandard}' # appending standard command to singularity image execution command
        print(f'\nRunning DSI Studio src standard action for subject: {subjID}.....\n')
        print(fullCommandStandard)
        os.system(fullCommandStandard)
        print(f'\n{subjID} standard src exited!\n')

        fullCommandReversed = f'{singularityCommand} {srcCommandReversed}' # appending reversed command to singularity image execution command
        print(f'\nRunning DSI Studio src reversed action for subject: {subjID}.....\n')
        print(fullCommandReversed)
        os.system(fullCommandReversed)
        print(f'\n{subjID} reversed src exited!\n')

reconOutputDirectory = os.path.join(pipelineDirectory, 'fib')
for subjID in os.listdir(outputDirectorySRC):
    start = time.time()
    subInputDir = os.path.join(outputDirectorySRC, subjID)
    subjRecOutDirectory = os.path.join(reconOutputDirectory, subjID) # fib/subject/
    try:
        os.mkdir(subjRecOutDirectory)
    except FileExistsError:
        print(f'\nrecon action already complete for subject: {subjID}.....\n')
        continue

    for ses in subInputDir:
        currSesSRCDir = os.path.join(subInputDir, ses)
        subjRecOutDirectory = os.path.join(reconOutputDirectory, subjID) # fib/subject/
        
        # src files for input
        for file in os.listdir(currSesSRCDir):
            if 'rev' in file:
                revFileName = file
            elif 'std' in file:
                stdFileName = file
        srcFileS = os.path.join(currSesSRCDir, stdFileName)
        srcFileR = os.path.join(currSesSRCDir, revFileName)
        fibFileOutput = os.path.join(subjRecOutDirectory, f'{subjID}_{ses}_rec.icbm152_adult.qsdr.1.25.fib.gz')

        

        settings = '--method=7 --param0=1.25 --template=0 --qsdr_reso=2.0' # optional settings flags
        reconCommand = f'dsi_studio --action=rec --source={srcFileS} --rev_pe={srcFileR} --output={fibFileOutput} {settings}'

        fullRecCommand = f'{singularityCommand} {reconCommand}'
        print(f'\nRunning DSI Studio recon action for subject: {subjID}.....\n')
        os.chdir(os.path.join(outputDirectorySRC, subjID))
        print(fullRecCommand)
        os.system(fullRecCommand)
        end = time.time()
        print(f'\n{subjID} recon exited in {end - start} seconds!\n')
        os.chdir(pipelineDirectory)