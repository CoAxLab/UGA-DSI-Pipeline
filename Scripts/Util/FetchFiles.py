import os

pipelineDir = os.getcwd()
figures = os.path.join(pipelineDir, 'Figures')

def FetchFigures()->tuple[list, list, list]:
    '''
    Returns tuple of lists that contain full file path for figures:
        ([T1wFiles], [T2wFiles], [dwiFiles])
    '''
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