import os

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryNifti = os.path.join(pipelineDirectory, 'nifti')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')

singularityCommand = f'singularity exec {sifFile}'

## run src process using b10, b2000, b4000 for each subject
for subjID in os.listdir(sourceDirectoryNifti):
    # source files:
    b10File = os.path.join(sourceDirectoryNifti, subjID, 'b10_hyper3.nii.gz')
    b2000File = os.path.join(sourceDirectoryNifti, subjID, 'b2000_hyper3.nii.gz')
    b4000File = os.path.join(sourceDirectoryNifti, subjID, 'b4000_hyper3.nii.gz')
    # output file:
    srcFile = os.path.join(outputDirectorySRC, subjID, f'{subjID}_hyper3.nii.gz.src.gz')
    try:
        os.mkdir(os.path.join(outputDirectorySRC, subjID))
    except FileExistsError:
        print(f'\nsrc standard action already complete for subject: {subjID}!\n')
        continue
    srcCommandStandard = f'dsi_studio --action=src --source={b10File} --other_source={b2000File},{b4000File} --output={srcFile}'

    # reversed source files:
    b10FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b10_hyper3.nii.gz')
    b2000FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b2000_hyper3.nii.gz')
    b4000FileR = os.path.join(sourceDirectoryNifti, subjID, 'x_b4000_hyper3.nii.gz')
    # reversed output file:
    srcFileR = os.path.join(outputDirectorySRC, subjID, f'{subjID}_x_hyper3.nii.gz.src.gz')
    try:
        os.mkdir(os.path.join(outputDirectorySRC, subjID))
    except FileExistsError:
        print(f'\nsrc reversed action already complete for subject: {subjID}!\n')
        continue

    srcCommandReversed = f'dsi_studio --action=src --source={b10FileR} --other_source={b2000FileR},{b4000FileR} --output={srcFileR}'

    fullCommandS = f'{singularityCommand} {srcCommandStandard}'
    print(f'\nRunning DSI Studio src standard action for subject: {subjID}.....\n')
    os.system(fullCommandS)
    print(f'\n{subjID} standard src complete!\n')

    fullCommandR = f'{singularityCommand} {srcCommandReversed}'
    print(f'\nRunning DSI Studio src reversed action for subject: {subjID}.....\n')
    os.system(fullCommandR)
    print(f'\n{subjID} reversed src complete!\n')

reconOutputDirectory = os.path.join(pipelineDirectory, 'fib')
for subjID in os.listdir(outputDirectorySRC):
    # src files for input
    srcFileS = os.path.join(pipelineDirectory, 'src', subjID, f'{subjID}_hyper3.nii.gz.src.gz')
    srcFileR = os.path.join(pipelineDirectory, 'src', subjID, f'{subjID}_x_hyper3.nii.gz.src.gz')
    # fib output file
    subjRecOutDirectory = os.path.join(reconOutputDirectory, subjID)
    try:
        os.mkdir(subjRecOutDirectory)
    except FileExistsError:
        print(f'\nrecon action already complete for subject: {subjID}.....\n')
        continue
    #fibFile = os.path.join(reconOutputDirectory, subjID, f'{subjID}_')
    settings = '--cmd="[Step T2][Corrections][TOPUP EDDY]+[Step T2][Corrections][EDDY]" --method=4 --param0=1.25 --motion_correction=1 --method=7 --param0=1.00 --template=0'
    reconCommand = f'dsi_studio ==action=rec --source={srcFileS} rev_pe={srcFileR} {settings} --output={subjRecOutDirectory}'

    fullRecCommand = f'{singularityCommand} {reconCommand}'
    print(f'\nRunning DSI Studio recon action for subject: {subjID}.....\n')
    os.system(fullRecCommand)
    print(f'\n{subjID} recon complete!\n')