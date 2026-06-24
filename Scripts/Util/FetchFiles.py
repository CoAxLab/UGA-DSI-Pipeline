import os
import pandas as pd
from Scripts.AnalysisScripts import qualityDistributions
from Scripts.Util import Debug

pipelineDir = os.getcwd()
figures = os.path.join(pipelineDir, 'Output', 'Figures')
fibFiles = os.path.join(pipelineDir, 'Output', 'fib')

def MakeFigures()->tuple[dict, dict, dict]:
    t1Dict, t2Dict = qualityDistributions.RunAnatomical()
    dwiDict = qualityDistributions.RunFunctional()
    return t1Dict, t2Dict, dwiDict

def FetchDFs()->tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    '''
    Returns tuple of dataframes that contain figure meta data:
        ([T1wMeta], [T2wMeta], [dwiMeta])
    '''
    t1, t2, dwi = None, None, None
    if os.path.isdir(figures):
        #raise Exception(f'Figures not set up.')
        for f in os.listdir(figures):
            if '.csv' in f:
                fPath = os.path.join(figures, f)
                if 'T1w' in f:
                    t1 = pd.read_csv(fPath)
                elif 'T2w' in f:
                    t2 = pd.read_csv(fPath)
                elif 'diffusion' in f:
                    dwi = pd.read_csv(fPath)

    if t1 is None: t1 = pd.DataFrame()
    if t2 is None: t2 = pd.DataFrame()
    if dwi is None: dwi = pd.DataFrame()

    return t1, t2, dwi

def FetchFigures()->tuple[list, list, list]:
    '''
    Returns tuple of lists that contain full file path for figures:
        ([T1wFiles], [T2wFiles], [dwiFiles])
    '''
    #MakeFigures()
    t1, t2, dwi = [], [], []
    if os.path.isdir(figures):
        #raise Exception(f'Figures not set up.')
        for f in os.listdir(figures):
            if '.png' in f:
                fPath = os.path.join(figures, f)
                if 'T1w' in f:
                    t1.append(fPath)
                elif 'T2w' in f:
                    t2.append(fPath)
                elif 'dwi' in f:
                    dwi.append(fPath)
    return t1, t2, dwi

def OpenFibFile(subSes:str)->None:
    path = os.path.join(fibFiles, subSes)
    if not os.path.isdir(path):
        Debug.Log(f'WARNING: target directory does not exist!\n\t{path}', True)
        return
    for file in os.listdir(path):
        if '.fib' in file or '.fz' in file:
            pathToFib = os.path.join(path, file)
            print(f'dsi_studio --action=trk --fib={pathToFib}')
            #os.system(f'dsi_studio --action=trk --fib={pathToFib}')
            return
    Debug.Log(f'WARNING: target directory exists, but no fib file found!\n\t{path}', True)
    return