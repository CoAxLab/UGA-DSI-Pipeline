import os
from bids_validator import BIDSValidator

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryNifti = os.path.join(pipelineDirectory, 'nifti')
outDirectoryQC = os.path.join(pipelineDirectory, 'QCOutput')
try:
    os.mkdir(outDirectoryQC)
except FileExistsError:
    print(f'Directory:\n\t{outDirectoryQC}\nalready exists!')
sifFile = os.path.join(sifDirectory, 'mriqc_latest.sif')
singularityCommand = f'singularity exec {sifFile}'

print(BIDSValidator().is_bids(sourceDirectoryNifti))
# for subjID in os.listdir(sourceDirectoryNifti):
#     if subjID[0:3] != 'sub': 
#         print(f'skipping {subjID}')
#         continue
#     nextDir = os.path.join(sourceDirectoryNifti, subjID)
#     print(BIDSValidator().is_bids(nextDir))
#     print(nextDir)
    # try:
    #     for file in os.listdir(nextDir):
    #         print(BIDSValidator().is_bids(os.path.join(nextDir, file)))
    # except NotADirectoryError:
    #     print('not a directory')
    
   
qcCommand = f'{singularityCommand} mriqc {sourceDirectoryNifti} {outDirectoryQC} participant'
os.system(qcCommand)