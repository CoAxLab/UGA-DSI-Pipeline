import os

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryBids = os.path.join(pipelineDirectory, 'qcBIDS')
outDirectoryQC = os.path.join(pipelineDirectory, 'QCOutput')
workDirectory = os.path.join(pipelineDirectory, 'work')
try:
    os.mkdir(outDirectoryQC)
    os.mkdir(workDirectory)
except FileExistsError:
    print(f'Directory:\n\t{outDirectoryQC}\nos\n{workDirectory}\nalready exists!')
sifFile = os.path.join(sifDirectory, 'mriqc_latest.sif')
singularityCommand = f'singularity exec --bind {sourceDirectoryBids}:/qcBIDS --bind {outDirectoryQC}:/QCOutput --bind {workDirectory}:/work {sifFile}'


for subjID in os.listdir(sourceDirectoryBids):
    if subjID in ['participants.tsv', 'dataset_description.json']:
        continue
    print(subjID)
    subDir = os.path.join(sourceDirectoryBids, subjID)
    subjectSTR = subjID[4:]
    for ses in os.listdir(subDir):
        sessionSTR = ses[4:]
        qcCommand = f'{singularityCommand} mriqc /qcBIDS /QCOutput participant --participant_label {subjectSTR} --session-id {sessionSTR} -w /work'
        print(f'-=-=-Running MRIQC for {subjID} {ses}\n    {qcCommand}')
        os.system(qcCommand)
