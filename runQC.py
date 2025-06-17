import os

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryBids = os.path.join(pipelineDirectory, 'BIDS')
outDirectoryQC = os.path.join(pipelineDirectory, 'QCOutput')
workDirectory = os.path.join(pipelineDirectory, 'work')
try:
    os.mkdir(outDirectoryQC)
    os.mkdir(workDirectory)
except FileExistsError:
    print(f'Directory:\n\t{outDirectoryQC}\nos\n{workDirectory}\nalready exists!')
sifFile = os.path.join(sifDirectory, 'mriqc_latest.sif')
singularityCommand = f'singularity exec --bind {sourceDirectoryBids}:/BIDS --bind {outDirectoryQC}:/QCOutput --bind {workDirectory}:/work {sifFile}'


for subjID in os.listdir(sourceDirectoryBids):
    if subjID in ['participants.tsv', 'dataset_description.json']:
        continue
    print(f'\n\n\n\nsubjID\n\n\n\n')
    subDir = os.path.join(sourceDirectoryBids, subjID)
    subjectSTR = subjID[4:]
    for ses in os.listdir(subDir):
        print(f'\n\n\n\n{subjID}_{ses}\n\n\n\n')
        sessionSTR = ses[4:]
        try:
            os.mkdir(os.path.join(workDirectory, f'{subjID}_{ses}'))
        except FileExistsError:
            print(f'skipping {subjID}\'s {ses}')
            continue
        qcCommand = f'{singularityCommand} mriqc /BIDS /QCOutput participant --participant_label {subjectSTR} --session-id {sessionSTR} --modalities T1w T2w --nprocs 48 --mem-gb 62 -w /work/{subjID}_{ses} --no-sub'
        print(f'-=-=-Running MRIQC for {subjID} {ses}\n    {qcCommand}')
        os.system(qcCommand)

# QCCommand = f'{singularityCommand} mriqc /BIDS /QCOutput participant --modalities T1w T2w --nprocs 48 --mem-gb 62 -w /work'
# print(f'-----Running MRIQC for all subjects:\n\t{QCCommand}')
# os.system(QCCommand)