import os
from Scripts.Util import Debug
pipelineDirectory = os.getcwd()
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')

def FlipLOWBLocation()->str:
    '''
    Moves low-b files either to the lowBFiles dir or the BIDS dir.
    Target directory is determined by location of first lowB files encountered.
        -This will un-scatter the files
    Returns string of target location -> ('BIDS' or 'lowBFiles')
    '''
    toBids = False
    toLowB = False
    print(f'Moving low-b files. Outputs should all match.')
    for id in os.listdir(parentBIDS):
        subBIDS = os.path.join(parentBIDS, id)
        if os.path.isdir(subBIDS) == False:
            continue
        # attempts to move lowb files to BIDS directory
        for ses in os.listdir(subBIDS):

            dwiPath = os.path.join(subBIDS, ses, 'dwi')
            lowBPath = dwiPath.replace('BIDS', 'lowBFiles')
            if os.listdir(lowBPath) != []: ### if lowBFiles has the files, then move them to BIDS folder
                if toLowB == True: 
                    Debug.Log(f"Low b files are scattered. Skipping {id}, {ses} to fix.")
                    continue
                if os.path.isdir(lowBPath) == False:
                    Debug.Log(f'{id}, {ses} has no LowB dwi path, skipping')
                    continue
                toBids = True
                for f in os.listdir(lowBPath):
                    lowBFile = os.path.join(lowBPath, f)
                    target = os.path.join(dwiPath, f)
                    os.system(f'mv {lowBFile} {target}')
                    print(f'Sub: {id}: Moved file to BIDS/')
            else: ### lowBFiles does not have the files, move them here
                if toBids == True: 
                    Debug.Log(f"Low b files are scattered. Skipping {id}, {ses} to fix.")
                    continue
                if os.path.isdir(dwiPath) == False:
                    Debug.Log(f'{id}, {ses} has no BIDS dwi path, skipping')
                    continue
                toLowB = True
                for f in os.listdir(dwiPath):
                    if 'lowb' in f:
                        lowBFile = os.path.join(dwiPath, f)
                        target = os.path.join(lowBPath, f)
                        os.system(f'mv {lowBFile} {target}')
                        print(f'Sub {id}: Moved file to lowBFiles/')
    if toBids:
        return 'Low-B files moved to BIDS/'
    if toLowB:
        return 'Low-B files moved to lowBFiles/'
    else:
        return 'No files have moved!'