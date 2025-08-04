import os
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()
nifti = os.path.join(pipelineDirectory, 'convertToBids')
bids = os.path.join(pipelineDirectory, 'BIDS')
lowB = os.path.join(pipelineDirectory, 'lowBFiles')
qc = os.path.join(pipelineDirectory, 'QCOutput')
src = os.path.join(pipelineDirectory, 'src')
fib = os.path.join(pipelineDirectory, 'fib')

def compareContents(source:str, target:str)->tuple[set, set, set]:
    if os.path.isdir(source) == False:
        Debug.Log(f'{source}\nis empty.')
        return set(), set(), set()
    
    sourceSet = set()
    if target != 'src':
        for f in os.listdir(source):
            if '.' in f:
                continue
            for remove in ['sub-', '_', 'ses-1', 'ses-2']:
                f = f.replace(remove, '')
            sourceSet.add(f)
    else: # case for when checking BIDS against src
        for f in os.listdir(source):
            subDir = os.path.join(source, f)
            if os.path.isdir(subDir) == False:
                continue
            for ses in os.listdir(subDir):
                addThis = f'{f}_{ses}'
                for remove in ['sub-', '_', 'ses-1', 'ses-2']:
                    addThis = addThis.replace(remove, '')
                sourceSet.add(addThis)

    if os.path.isdir(target) == False:
        return sourceSet, sourceSet, set()
    
    targetSet = set()
    Debug.Log(f'{target}')
    for f in os.listdir(target):
        Debug.Log(f'{f}')
        if '.' in f:
            continue
        for remove in ['sub-', '_', 'ses-1', 'ses-2']:
            f = f.replace(remove, '')
        targetSet.add(f)
    
    return sourceSet, sourceSet - targetSet, targetSet

def niftiStatus()->tuple[set, set, set]:
    '''
    Returns set of ID strings that will be run if nifti to bids is called
    '''
    return compareContents(nifti, bids)

def qcStatus()->tuple[set,set,set]:
    '''
    Returns set of ID strings that will be run if QC is called
    '''
    return compareContents(bids, qc)

def srcStatus()->tuple[set,set,set]:
    '''
    Returns set of ID strings that will be run if src is called
    '''
    return compareContents(bids, src)

def recStatus()->tuple[set,set,set]:
    '''
    Returns set of ID strings that will be run if rec is called
    '''
    return compareContents(src, fib)