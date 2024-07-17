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
        print(f'\nsrc action already complete for subject: {subjID}!\n')
        continue

    srcCommand = f'dsi_studio --action=src --source={b10File} --other_source={b2000File},{b4000File} --output={srcFile}'

    fullCommand = f'{singularityCommand} {srcCommand}'
    print(f'\nRunning DSI Studio src action for subject: {subjID}.....\n')
    os.system(fullCommand)
    print(f'\n{subjID} complete!\n')