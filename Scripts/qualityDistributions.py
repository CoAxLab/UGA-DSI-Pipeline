import os, json, csv, statistics, argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

'''
Handle command line arguments
'''
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

'''
Globals and setup
'''
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

'''
Functions
'''

def hasOutlier(dataList: list) -> tuple:
    '''
    given a list of numeric data...
    returns tuple: (Bool: <is there an outlier?>, Int <outlier index>)
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

    maxZ = maxDifference / dataSD
    a = .05
    gCritical = stats.t.ppf((1 + (1 - a))/2, len(dataList) - 2)

    return (maxZ > gCritical, index)


def makeOutlierLists(dictOfMeasures: dict) -> None:
    '''
    give dictionary where keys correspond to lists of numeric data...
    make a list for each measure, value is 1 if measure has outlier at this index, 0 if not
    ignores Primary Key ('source_id')
    '''
    allMeasures = list(dictOfMeasures.keys())
    for measure in allMeasures:
        if measure == 'source_id': continue
        doLoop, location = hasOutlier(dictOfMeasures[measure])
        flaggedValues = set()
        listCopy = dictOfMeasures[measure][0:]
        while doLoop:
            # only enters if one outlier is found. Will check and remove until none exist
            flaggedValues.add(listCopy[location])
            listCopy.pop(location)
            doLoop, location = hasOutlier(listCopy)
        
        outliersList = []
        for j, value in enumerate(dictOfMeasures[measure]):
            if value in flaggedValues:
                outliersList.append(1)
                print(f'Flagged value: {value}, loc: {j} as outlier for measure: {measure}')
            else:
                outliersList.append(0)
        dictOfMeasures[f'{measure}_Outliers'] = outliersList
    print(f'Created {len(dictOfMeasures) - len(allMeasures)} new keys')
    return


if runFunc == True:

    diffusionMeasures = {
        'coherence_index': [],
        'R2_qsdr': []
    }
    namesDiffusion = set(diffusionMeasures.keys())
    diffusionMeasures['source_id'] = []

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

        #print(f'\nCOMPLETED {subjectSession}. Moving on...\n\n')

    makeOutlierLists(diffusionMeasures)
    dwi_exmDF = pd.DataFrame(diffusionMeasures)
    dwi_exmDF.to_csv(os.path.join(figuresOutput, 'diffusionDF.csv'))

    for m in namesDiffusion:
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
            hue = f'{m}_Outliers',
            palette = 'magma',
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
        'snr_total': [],
        'snr_csf': [],
        'snr_gm': [],
        'qi_2': [],
        'rpve_gm': [],
        'rpve_wm': [],
        'rpve_csf': []
    }
    namesAnatomical = set(extractedMeasures.keys())
    extractedMeasures['source_id'] = []
        
    for sub in os.listdir(qcOutputDirectory):
        if 'logs' in sub: continue
        currSub = os.path.join(qcOutputDirectory, sub)
        if os.path.isdir(currSub) == False: continue
        for ses in os.listdir(currSub):
            if 'figures' in ses: continue
            currSesAnat = os.path.join(currSub, ses, 'anat')
            for file in os.listdir(currSesAnat):
                if '.json' not in file: continue
                extractedMeasures['source_id'].append(file)
                jsonPath = os.path.join(currSesAnat, file)
                f = open(jsonPath, 'r')
                metrics = json.load(f)
                for key in extractedMeasures:
                    if key == 'source_id': continue
                    extractedMeasures[key].append(metrics[key])

    makeOutlierLists(extractedMeasures)
    exmDF = pd.DataFrame(extractedMeasures)
    exmDF.to_csv(os.path.join(figuresOutput, 'anatomicalDF.csv'))

    for m in namesAnatomical:
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
            hue = f'{m}_Outliers',
            palette= 'magma',
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