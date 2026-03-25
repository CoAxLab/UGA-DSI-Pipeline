import os
import pandas as pd
from Scripts import qualityDistributions

pipelineDir = os.getcwd()
figures = os.path.join(pipelineDir, 'Figures')

def MakeFigures()->tuple[dict, dict, dict]:
    t1Dict, t2Dict = qualityDistributions.RunAnatomical()
    dwiDict = qualityDistributions.RunFunctional()
    return t1Dict, t2Dict, dwiDict

def FetchDFs()->tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    '''
    Returns tuple of dataframes that contain figure meta data:
        ([T1wMeta], [T2wMeta], [dwiMeta])
    '''
    for f in os.listdir(figures):
        if '.csv' in f:
            fPath = os.path.join(figures, f)
            if 'T1w' in f:
                t1 = pd.read_csv(fPath)
            elif 'T2w' in f:
                t2 = pd.read_csv(fPath)
            elif 'diffusion' in f:
                dwi = pd.read_csv(fPath)
    return t1, t2, dwi

def FetchFigures()->tuple[list, list, list]:
    '''
    Returns tuple of lists that contain full file path for figures:
        ([T1wFiles], [T2wFiles], [dwiFiles])
    '''
    #MakeFigures()
    t1, t2, dwi = [], [], []
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