import os

pipelineDirectory = os.getcwd()
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
if not os.path.isdir(bidsDirectory):
    raise Exception(f'ERROR: Please run the following:\n\tsetupPipeline.py, move data to convertToBids, and run niftiToBids.py\nbefore attempting to run the pipeline!')

os.system('python runQC.py')
os.system('python runPipeline.py')