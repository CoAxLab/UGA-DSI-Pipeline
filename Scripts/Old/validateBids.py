import os
from bids_validator import BIDSValidator

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryBids = os.path.join(pipelineDirectory, 'BIDS')
outDirectoryQC = os.path.join(pipelineDirectory, 'QCOutput')
try:
    os.mkdir(outDirectoryQC)
except FileExistsError:
    print(f'Directory:\n\t{outDirectoryQC}\nalready exists!')
sifFile = os.path.join(sifDirectory, 'mriqc_latest.sif')
singularityCommand = f'singularity exec {sifFile}'

BIDSValidator().is_bids(sourceDirectoryBids)
print(BIDSValidator().is_bids(sourceDirectoryBids))

for subjID in os.listdir(sourceDirectoryBids):
    print(subjID)
    currBidsDir = os.path.join(sourceDirectoryBids, subjID)
    print(currBidsDir)
    BIDSValidator().is_bids(currBidsDir)
    print(BIDSValidator().is_bids(currBidsDir))