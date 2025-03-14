import os
#from bids_validator import BIDSValidator

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


# for subjID in os.listdir(sourceDirectoryBids):
#     if subjID in ['participants.tsv', 'dataset_description.json']:
#         continue
#    print(subjID)
#    currBidsDir = os.path.join(sourceDirectoryBids, subjID)
#print(BIDSValidator().is_bids(currBidsDir))
qcCommand = f'{singularityCommand} mriqc {sourceDirectoryBids} {outDirectoryQC} participant'
os.system(qcCommand)