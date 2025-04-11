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

    for sesDir in os.listdir(subBidsPath):
        subSesTag = f'{subjID}_{sesDir}'
        subSesSRCDir = os.path.join(outputDirectorySRC, subSesTag)
        os.mkdir(subSesSRCDir)
        # source files:
        lowStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-lowb_dwi.nii.gz')
        midStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-midb_dwi.nii.gz')
        highSandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-std_acq-highb_dwi.nii.gz')
        # output file:
        stdOutFile = os.path.join(subSesSRCDir, f'{subjID}_{sesDir}_dir-std.src.gz')
        srcCommandStandard = f'dsi_studio --action=src --source={lowStandard} --other_source={midStandard},{highSandard} --output={stdOutFile}'

        # reversed source files:
        lowReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-lowb_dwi.nii.gz')
        midReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-midb_dwi.nii.gz')
        highReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-highb_dwi.nii.gz')
        # reversed output file:
        revOutFile = os.path.join(subSesSRCDir, f'{subjID}_{sesDir}_dir-rev.src.gz')

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
for subSesID in os.listdir(outputDirectorySRC):
    start = time.time()
    srcInputDir = os.path.join(outputDirectorySRC, subSesID)
    recOutDirectory = os.path.join(reconOutputDirectory, subSesID) # fib/subjectsession/
    try:
        os.mkdir(recOutDirectory)
    except FileExistsError:
        print(f'\nrecon action already complete for subject: {subjID}.....\n')
        continue
        
    for file in os.listdir(srcInputDir):
        if 'rev' in file:
            revFileName = file
        elif 'std' in file:
            stdFileName = file
    srcFileS = os.path.join(srcInputDir, stdFileName)
    srcFileR = os.path.join(srcInputDir, revFileName)
    fibFileOutput = os.path.join(recOutDirectory, f'{subSesID}_rec.icbm152_adult.qsdr.1.25.fib.gz')

        

    settings = '--method=7 --param0=1.25 --template=0 --qsdr_reso=2.0' # optional settings flags
    reconCommand = f'dsi_studio --action=rec --source={srcFileS} --rev_pe={srcFileR} --output={fibFileOutput} {settings}'

    fullRecCommand = f'{singularityCommand} {reconCommand}'
    print(f'\nRunning DSI Studio recon action for subject: {subjID}.....\n')
    os.chdir(srcInputDir)
    print(fullRecCommand)
    os.system(fullRecCommand)
    end = time.time()
    print(f'\n{subjID} recon exited in {end - start} seconds!\n')
    os.chdir(pipelineDirectory)