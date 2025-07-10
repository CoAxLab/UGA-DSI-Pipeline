import os
import json
import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import seaborn as sns
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dwi', action='store_true', help='flag to only plot distributions for functional file QA values')
parser.add_argument('-s', '--structural', action='store_true', help='flag to only plot distributions for anatomical file QA values')
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
singularityCommand = f'singularity exec -B {fibDirectory}:/fib {sifFile}'

try:
    os.mkdir(figuresOutput)
except Exception as e:
    pass

if runFunc == True:
    allFDMeans = []
    for subjectSession in os.listdir(fibDirectory):
        thisdir = os.path.join(fibDirectory, subjectSession)
        try:
            fname = os.listdir(thisdir)[0]
        except Exception as e:
            print(f'\n{e}\n\tDirectory Empty For {subjectSession}!!!\n\tContinuing.....')
            continue

        qcCommandPart = f'dsi_studio --action=qc --source=/fib/{subjectSession}/{fname} --check_rotation --check_snr --check_eddy --check_iso'
        
        fullCommandQC = f'{singularityCommand} {qcCommandPart}'
        if len(os.listdir(thisdir)) == 1: # if qa file is NOT already extracted
            print(f'{fullCommandQC}')
            os.system(fullCommandQC)
        else:
            print(f'Looks like qa file for {subjectSession} has already been exported!\nNot running export action...')
        print(f'\nCOMPLETED {subjectSession}. Moving on...\n\n')
    #     for file in os.listdir(thisdir):
    #         if '.nii.gz' not in file: continue
    #         qaZipPath = os.path.join(thisdir, file)
    #         #qaFName = os.listdir(qaZipPath)[0]
    #         #qaFile = os.path.join(qaZipPath, qaFName)

    #         object = nib.load(qaZipPath)
    #         qaData = object.get_fdata()

    #         print(f'number of qa metrics: {qaData.shape[-1]}\n{file}\n')
    #         for i in range(len(qaData)):
    #             metric = qaData[..., i]
    #             print(f'metric {i},\nmean = {metric.mean()},\nrange = [{metric.min()} {metric.max()}]')
    # print(allFDMeans)

extractedMeasures = {
    'snr_total': [],
    'snr_csf': [],
    'snr_gm': [],
    'qi_2': [],
    'rpve_gm': [],
    'rpve_wm': [],
    'rpve_csf': []
}

if runAnat == True:
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

        sns.catplot(
            x = extractedMeasures[m],
            kind = 'violin',
            inner = 'quart',
            color = "#FBECFD2F"
            )
        
        sns.stripplot(
            x = extractedMeasures[m],
            color = "#7D009C",
            edgecolor = "#000000",
            linewidth = 1,
            size = 6
        )

        n = len(extractedMeasures[m])
        outPath = os.path.join(figuresOutput, f'{m}_distribution_n{n}.png')
        plt.title(m)
        sns.despine()
        plt.savefig(outPath)