import os
import time

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryNifti = os.path.join(pipelineDirectory, 'bids')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')

singularityCommand = f'singularity exec {sifFile}'

## run src process using b10, b2000, b4000 for each subject
for subjID in os.listdir(sourceDirectoryNifti):
    # source files:
    b10File = os.path.join(sourceDirectoryNifti, subjID, f'sub-{subjID}', 'dwi' , 'b10_hyper3.nii.gz')
    b2000File = os.path.join(sourceDirectoryNifti, subjID, 'b2000_hyper3.nii.gz')
    b4000File = os.path.join(sourceDirectoryNifti, subjID, 'b4000_hyper3.nii.gz')
    # output file:
    srcFile = os.path.join(outputDirectorySRC, subjID, f'{subjID}_hyper3.nii.gz.src.gz')
    try:
        os.mkdir(os.path.join(outputDirectorySRC, subjID))
    except FileExistsError:
        print(f'\nsrc action already complete for subject: {subjID}!\n')
        continue
    srcCommandStandard = f'dsi_studio --action=src --source={b10File} --other_source={b2000File},{b4000File} --output={srcFile}'

    # reversed source files:
    b10FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b10_hyper3.nii.gz')
    b2000FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b2000_hyper3.nii.gz')
    b4000FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b4000_hyper3.nii.gz')
    # reversed output file:
    srcFileR = os.path.join(outputDirectorySRC, subjID, f'{subjID}_x_hyper3.nii.gz.src.gz')

    srcCommandReversed = f'dsi_studio --action=src --source={b10FileR} --other_source={b2000FileR},{b4000FileR} --output={srcFileR}'

    fullCommandS = f'{singularityCommand} {srcCommandStandard}'
    print(f'\nRunning DSI Studio src standard action for subject: {subjID}.....\n')
    os.system(fullCommandS)
    print(f'\n{subjID} standard src exited!\n')

    fullCommandR = f'{singularityCommand} {srcCommandReversed}'
    print(f'\nRunning DSI Studio src reversed action for subject: {subjID}.....\n')
    os.system(fullCommandR)
    print(f'\n{subjID} reversed src exited!\n')

reconOutputDirectory = os.path.join(pipelineDirectory, 'fib')
for subjID in os.listdir(outputDirectorySRC):
    start = time.time()
    # src files for input
    srcFileS = os.path.join(pipelineDirectory, 'src', subjID, f'{subjID}_hyper3.nii.gz.src.gz')
    srcFileR = os.path.join(pipelineDirectory, 'src', subjID, f'{subjID}_x_hyper3.nii.gz.src.gz')
    # fib output file
    subjRecOutDirectory = os.path.join(reconOutputDirectory, subjID)
    fibFileOutput = os.path.join(subjRecOutDirectory, f'{subjID}_hyper3.icbm152_adult.qsdr.1.25.fib.gz')
    try:
        os.mkdir(subjRecOutDirectory)
    except FileExistsError:
        print(f'\nrecon action already complete for subject: {subjID}.....\n')
        continue
    #fibFile = os.path.join(reconOutputDirectory, subjID, f'{subjID}_')
    #settings = '--method=7 --param0=1.25 --template=0 --qsdr_reso=2.0'
    reconCommand = f'dsi_studio --action=rec --source={srcFileS} --rev_pe={srcFileR} --output={fibFileOutput}'

    fullRecCommand = f'{singularityCommand} {reconCommand}'
    print(f'\nRunning DSI Studio recon action for subject: {subjID}.....\n')
    os.chdir(os.path.join(outputDirectorySRC, subjID))
    os.system(fullRecCommand)
    end = time.time()
    print(f'\n{subjID} recon exited in {end - start} seconds!\n')
