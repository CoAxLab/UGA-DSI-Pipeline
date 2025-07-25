import os
pipelineDirectory = os.getcwd()
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')

def FlipLOWBLocation()->None:
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
                if toLowB == True: raise Exception("Major issue: Low b files are scattered. Contact pipeline maintainer.")
                toBids = True
                for f in os.listdir(lowBPath):
                    lowBFile = os.path.join(lowBPath, f)
                    target = os.path.join(dwiPath, f)
                    os.system(f'mv {lowBFile} {target}')
                    print(f'Sub: {id}: Moved file to BIDS/')
            else: ### lowBFiles does not have the files, move them here
                if toBids == True: raise Exception("Major issue: Low b files are scattered. Contact pipeline maintainer.")
                toLowB = True
                for f in os.listdir(dwiPath):
                    if 'lowb' in f:
                        lowBFile = os.path.join(dwiPath, f)
                        target = os.path.join(lowBPath, f)
                        os.system(f'mv {lowBFile} {target}')
                        print(f'Sub {id}: Moved file to lowBFiles/')