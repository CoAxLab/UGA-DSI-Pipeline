import os

pipelineDir = os.getcwd()
figures = os.path.join(pipelineDir, 'Figures')

def FetchFigures()->tuple[set, set, set]:
    '''
    Returns tuple of sets that contain full file path for figures:
        ({T1wFiles}, {T2wFiles}, {dwiFiles})
    '''
    t1, t2, dwi = set(), set(), set()
    for f in os.listdir(figures):
        if '.png' in f:
            fPath = os.path.join(figures, f)
            if 'T1w' in f:
                t1.add(fPath)
            elif 'T2w' in f:
                t2.add(fPath)
            elif 'dwi' in f:
                dwi.add(fPath)
    return t1, t2, dwi