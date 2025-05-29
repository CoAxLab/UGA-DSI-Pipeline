import os
pipelineDirectory = os.getcwd()
parentBIDS = os.path.join(pipelineDirectory, 'BIDS')
lowDir = os.path.join(pipelineDirectory, 'lowBFiles')

try:
    os.mkdir(lowDir)
except FileExistsError:
    print(f'Path:\n\t{lowDir}\nalready exists. Exiting.')

for id in os.listdir(parentBIDS):
    subLow = os.path.join(lowDir, id)
    subBIDS = os.path.join(parentBIDS, id)
    if os.path.isdir(subBIDS) == False: continue
    os.mkdir(subLow)
    for ses in os.listdir(subBIDS):
        sesLow = os.path.join(subLow, ses)
        sesBIDS = os.path.join(subBIDS, ses)
        os.mkdir(sesLow)
        os.mkdir(os.path.join(sesLow, 'dwi'))