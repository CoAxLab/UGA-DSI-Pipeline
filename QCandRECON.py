import os

pipelineDirectory = os.getcwd()
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
if not os.path.isdir(bidsDirectory):
    raise Exception(f'ERROR: Please run the following:\n\tsetupPipeline.py, move data to convertToBids, and run niftiToBids.py\nbefore attempting to run the pipeline!')

os.system('python runQC.py')
os.system('python runPipeline.py')

qcOut = os.path.join(pipelineDirectory, 'QCOutput')

if not os.path.isdir(qcOut):
    print(f'Attempting to run with "python3" command')
    os.system('python3 runQC.py')
    os.system('python3 runPipeline.py')

if not os.path.isdir(qcOut):
    raise Exception(f'ERROR: Pipeline has not run, missing dependencies or Python not on path as "python" or "python3"')