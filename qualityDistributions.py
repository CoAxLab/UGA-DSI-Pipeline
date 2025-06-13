import os
import json
import matplotlib.pyplot as plt

pipelineDirectory = os.getcwd()
figuresOutput = os.path.join(pipelineDirectory, 'Figures')
fibDirectory = os.path.join(pipelineDirectory, 'fib')
qcOutputDirectory = os.path.join(pipelineDirectory, 'QCOutput')
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')
singularityCommand = f'singularity exec {sifFile}'

try:
    os.mkdir(figuresOutput)
except Exception as e:
    pass

for subjectSession in os.listdir(fibDirectory):
    thisdir = os.path.join(fibDirectory, subjectSession)
    fname = os.listdir(thisdir)[0]
    fibFile = os.path.join(thisdir, fname)
    exportCommand = f'dsi_studio --action=exp --source={fibFile} --export=qa'
    
    fullCommand = f'{singularityCommand} {exportCommand}'
    print(f'{fullCommand}')
    os.system(fullCommand)

snrTotals = []
for sub in os.listdir(qcOutputDirectory):
    currSub = os.path.join(qcOutputDirectory, sub)
    if os.path.isdir(currSub) == False: continue
    for ses in os.listdir(currSub):
        if 'figures' in ses: continue
        currSesAnat = os.path.join(currSub, ses, 'anat')
        for file in os.listdir(currSesAnat):
            if '.json' not in file: continue
            jsonPath = os.path.join(currSesAnat, file)
            f = open(jsonPath, 'r')
            metrics = json.load(f)
            snrTotals.append(metrics["snr_total"])
plt.hist(snrTotals)
plt.savefig(os.path.join(figuresOutput, 'snrTotalDistribution.png'))