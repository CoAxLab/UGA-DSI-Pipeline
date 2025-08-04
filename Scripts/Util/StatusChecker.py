import os
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()
nifti = os.path.join(pipelineDirectory, 'convertToBids')
bids = os.path.join(pipelineDirectory, 'BIDS')
lowB = os.path.join(pipelineDirectory, 'lowBFiles')
qc = os.path.join(pipelineDirectory, 'QCOutput')
src = os.path.join(pipelineDirectory, 'src')
fib = os.path.join(pipelineDirectory, 'fib')

def compareContents(source:str, target:str)->set:
    if os.path.isdir(source) == False:
        Debug.Log(f'{source}\nis empty.')
        return set()
    
    sourceSet = set()
    if target != 'src':
        for f in os.listdir(source):
            if '.' in f:
                continue
            sourceSet.add(f)
    else: # case for when checking BIDS against src
        for f in os.listdir(source):
            subDir = os.path.join(source, f)
            if os.path.isdir(subDir) == False:
                continue
            for ses in os.listdir(subDir):
                sourceSet.add(f'{f}_{ses}')

    if os.path.isdir(target):
        return sourceSet
    
    targetSet = set()
    for f in os.listdir(target):
        if '.' in f:
            continue
        targetSet.add(f)
    
    return sourceSet - targetSet

def niftiStatus()->set:
    '''
    Returns set of ID strings that will be run if nifti to bids is called
    '''
    return compareContents(nifti, bids)

def qcStatus()->set:
    '''
    Returns set of ID strings that will be run if QC is called
    '''
    return compareContents(bids, qc)

def srcStatus()->set:
    '''
    Returns set of ID strings that will be run if src is called
    '''
    return compareContents(bids, src)

def qcStatus()->set:
    '''
    Returns set of ID strings that will be run if rec is called
    '''
    return compareContents(src, fib)