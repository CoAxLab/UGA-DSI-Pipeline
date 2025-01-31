import os
from bids_validator import BIDSValidator

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryBids = os.path.join(pipelineDirectory, 'bids')
outDirectoryQC = os.path.join(pipelineDirectory, 'QCOutput')
try:
    os.mkdir(outDirectoryQC)
except FileExistsError:
    print(f'Directory:\n\t{outDirectoryQC}\nalready exists!')
sifFile = os.path.join(sifDirectory, 'mriqc_latest.sif')
singularityCommand = f'singularity exec {sifFile}'


for subjID in os.listdir(sourceDirectoryBids):
    print(subjID)
    currBidsDir = os.path.join(sourceDirectoryBids, subjID)
    print(BIDSValidator().is_bids(currBidsDir))
    qcCommand = f'{singularityCommand} mriqc {currBidsDir} {outDirectoryQC} participant --participant-label {subjID}'
    os.system(qcCommand)
#     if subjID[0:3] != 'sub': 
#         print(f'skipping {subjID}')
#         continue
#     nextDir = os.path.join(sourceDirectoryBids, subjID)
#     print(BIDSValidator().is_bids(nextDir))
#     print(nextDir)
    # try:
    #     for file in os.listdir(nextDir):
    #         print(BIDSValidator().is_bids(os.path.join(nextDir, file)))
    # except NotADirectoryError:
    #     print('not a directory')
    
   
