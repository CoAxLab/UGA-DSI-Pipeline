import os
pipelineDirectory = os.getcwd()
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')

for id in os.listdir(parentBIDS):
    subBIDS = os.path.join(parentBIDS, id)
    if os.path.isdir(subBIDS) == False:
        continue
    # attempts to move lowb files to BIDS directory
    for ses in os.listdir(subBIDS):

        dwiPath = os.path.join(subBIDS, ses, 'dwi')
        lowBPath = dwiPath.replace('BIDS', 'lowBFiles')
        if os.path.isdir(lowBPath):
            for f in os.listdir(lowBPath):
                lowBFile = os.path.join(lowBPath, f)
                target = os.path.join(dwiPath, f)
                os.system(f'mv {lowBFile} {target}')