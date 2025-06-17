import os
import json
import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import seaborn as sns
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dwi', default=False, action='store_true', help='flag to only plot distributions for functional file QA values')
parser.add_argument('-s', '--structural', default=False, action='store_true', help='flag to only plot distributions for anatomical file QA values')
args = parser.parse_args()
if args.dwi == args.structural: # both are specified, or none specified
    runFunc = True
    runAnat = True
else:
    runFunc = args.dwi
    runAnat = args.structural

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

allFDMeans = []
for subjectSession in os.listdir(fibDirectory):
    thisdir = os.path.join(fibDirectory, subjectSession)
    try:
        fname = os.listdir(thisdir)[0]
    except Exception as e:
        print(f'\n{e}\n\tNothing under {subjectSession}...\n\tContinuing.....')
        continue
    inName = fname.replace('.gz', '')
    fibFile = os.path.join(thisdir, fname, inName)
    exportCommand = f'dsi_studio --action=exp --source={fibFile} --export=qa'
    
    fullCommand = f'{singularityCommand} {exportCommand}'
    print(f'{fullCommand}')
    os.system(fullCommand)

    for file in os.listdir(thisdir):
        if 'qa' not in file: continue
        qaZipPath = os.path.join(thisdir, file)
        qaFName = os.listdir(qaZipPath)[0]
        qaFile = os.path.join(qaZipPath, qaFName)

        object = nib.load(qaFile)
        qaData = object.get_fdata()

        if qaData.size == 1:
            fdMean = float(qaData)
            allFDMeans.append(fdMean)
        else:
            print(f'NEEDFIX')
print(allFDMeans)

extractedMeasures = {
    'snr_total': [],
    'snr_csf': [],
    'snr_gm': [],
    'qi_2': [],
    'rpve_gm': [],
    'rpve_wm': [],
    'rpve_csf': []
}

for sub in os.listdir(qcOutputDirectory):
    if 'logs' in sub: continue
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
            for key in extractedMeasures:
                extractedMeasures[key].append(metrics[key])

for m in extractedMeasures:
    plt.figure()
    plt.hist(extractedMeasures[m])
    outPath = os.path.join(figuresOutput, f'{m}_distribution.png')
    plt.title(m)
    sns.despine()
    plt.savefig(outPath)