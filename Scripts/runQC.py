import os
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()

sourceDirectoryBids = os.path.join(pipelineDirectory, 'Data', 'AnalysisData')
outDirectoryQC = os.path.join(pipelineDirectory, 'Output', 'QCOutput')
workDirectory = os.path.join(pipelineDirectory, 'Data','IntermediateData')



def RunMRIQC()->None:
    for needed in [outDirectoryQC, workDirectory]:
        try:
            os.mkdir(needed)
        except FileExistsError:
            Debug.Log(f'Directory:\n\t{needed}\nalready exists!')
    dockerCommand = f'docker run -it --rm -v {sourceDirectoryBids}:/BIDS -v {outDirectoryQC}:/QCOutput -v {workDirectory}:/work nipreps/mriqc:latest'


    for subjID in os.listdir(sourceDirectoryBids):
        if subjID in ['participants.tsv', 'dataset_description.json']:
            continue
        Debug.Log(f'\n\n{subjID} QC\n\n')
        subDir = os.path.join(sourceDirectoryBids, subjID)
        subjectSTR = subjID[4:]
        for ses in os.listdir(subDir):
            Debug.Log(f'\n\n{subjID}_{ses} QC\n\n')
            sessionSTR = ses[4:]
            try:
                os.mkdir(os.path.join(workDirectory, f'{subjID}_{ses}'))
            except FileExistsError:
                Debug.Log(f'Work directory for {subjID}\'s {ses} exists. Skipping...\n\tIf this is not intended, delete and re-run.')
                continue
            qcCommand = f'{dockerCommand} /BIDS /QCOutput participant --participant_label {subjectSTR} --session-id {sessionSTR} --modalities T1w T2w --nprocs 48 --mem-gb 62 -w /work/{subjID}_{ses} --no-sub'
            Debug.Log(f'-=-=-Running MRIQC for {subjID} {ses}\n    {qcCommand}')
            os.system(qcCommand)