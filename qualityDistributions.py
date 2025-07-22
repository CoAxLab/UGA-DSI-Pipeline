import os
import json
import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statistics
from scipy import stats
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


def hasOutlier(dataList):
    '''
    returns tuple: (Bool hasOutlier, Int outlierIndex)
    '''
    dataMean = sum(dataList) / len(dataList)
    dataSD = statistics.stdev(dataList)

    maxDifference = 0
    index = None
    for i, val in enumerate(dataList):
        candidate = abs(val - dataMean)
        if candidate > maxDifference:
            maxDifference = candidate
            index = i

    gStatistic = maxDifference / dataSD
    a = .05
    gCritical = stats.t.ppf((1 + (1 - a))/2, len(dataList) - 2)

    return (gStatistic > gCritical, index)


if runFunc == True:

    diffusionMeasures = {
        'source_id': [],
        'coherence_index': [],
        'R2_qsdr': []
    }

    for subjectSession in os.listdir(fibDirectory):
        thisdir = os.path.join(fibDirectory, subjectSession)
        try:
            fname = os.listdir(thisdir)[0]
        except Exception as e:
            print(f'\n{e}\n\tDirectory Empty For {subjectSession}!!!\n\tContinuing.....')
            continue

        qcCommandPart = f'dsi_studio --action=qc --source=/fib/{subjectSession}/{fname} --output=/fib/{subjectSession}/qc.tsv'
        
        fullCommandQC = f'{singularityCommand} {qcCommandPart}'

        if os.path.exists(os.path.join(thisdir, 'qc.tsv')) == False:
            print(f'{fullCommandQC}')
            os.system(fullCommandQC)

        qcFile = os.path.join(thisdir, 'qc.tsv')
        with open(qcFile, newline = '') as file:
            tsvObject = csv.reader(file, delimiter='\t')
            for r, row in enumerate(tsvObject):
                if r != 1: continue
                diffusionMeasures['source_id'].append(subjectSession)
                diffusionMeasures['coherence_index'].append(float(row[3]))
                diffusionMeasures['R2_qsdr'].append(float(row[4]))

        print(f'\nCOMPLETED {subjectSession}. Moving on...\n\n')

    dwi_exmDF = pd.DataFrame(diffusionMeasures)
    for m in diffusionMeasures:
        if m == 'source_id': continue
        plt.figure()

        sns.catplot(
            data = dwi_exmDF,
            x = m,
            kind = 'violin',
            inner = 'quart',
            color = "#ECFDFC2E"
            )
        
        sns.swarmplot(
            data = dwi_exmDF,
            x = m,
            #color = "#7D009C",
            hue = 'source_id',
            edgecolor = "#000000",
            linewidth = 1,
            size = 7
        )

        n = len(diffusionMeasures[m])
        outPath = os.path.join(figuresOutput, f'dwi_{m}_distribution_n{n}.png')
        plt.title(m)
        plt.legend().set_visible(False)
        sns.despine()
        plt.savefig(outPath, bbox_inches = 'tight')

if runAnat == True:
        
    extractedMeasures = {
        'source_file': [],
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
                extractedMeasures['source_file'].append(file)
                jsonPath = os.path.join(currSesAnat, file)
                f = open(jsonPath, 'r')
                metrics = json.load(f)
                for key in extractedMeasures:
                    if key == 'source_file': continue
                    extractedMeasures[key].append(metrics[key])

    exmDF = pd.DataFrame(extractedMeasures)
    for m in extractedMeasures:
        if m == 'source_file': continue
        plt.figure()

        sns.catplot(
            data = exmDF,
            x = m,
            kind = 'violin',
            inner = 'quart',
            color = "#FBECFD2F"
            )
        
        sns.swarmplot(
            data = exmDF,
            x = m,
            #color = "#7D009C",
            hue = 'source_file',
            edgecolor = "#000000",
            linewidth = 1,
            size = 7
        )

        n = len(extractedMeasures[m])
        outPath = os.path.join(figuresOutput, f'{m}_distribution_n{n}.png')
        plt.title(m)
        plt.legend().set_visible(False)
        sns.despine()
        plt.savefig(outPath, bbox_inches = 'tight')