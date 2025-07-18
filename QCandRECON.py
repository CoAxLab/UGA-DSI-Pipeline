import os

pipelineDirectory = os.getcwd()
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
if not os.path.isdir(bidsDirectory):
    raise Exception(f'ERROR: Please run the following:\n\tsetupPipeline.py, move data to convertToBids, and run niftiToBids.py\nbefore attempting to run the pipeline!')

def runScripts(python):
    os.system(f'{python} runQC.py')
    print(f'*****\nQC complete\n*****\nStarting lowB toggle script\n*****')
    os.system(f'{python} addLowBToBIDS.py')
    print(f'*****\nlowB move complete\n*****\nStarting DSI Studio pipeline\n*****')
    os.system(f'{python} runPipeline.py')
    print(f'*****\nDSI Studio actions complete\n*****\nStarting Quality Distributions\n*****')
    os.system(f'{python} qualityDistributions.py')
    print(f'*****\nQuality distributions complete!\n*****')

runScripts('python')
qcOut = os.path.join(pipelineDirectory, 'QCOutput')
if not os.path.isdir(qcOut):
    print(f'Attempting to run with "python3" command')
    runScripts('python3')

if not os.path.isdir(qcOut):
    raise Exception(f'ERROR: Pipeline has not run, missing dependencies or Python not on path as "python" or "python3"')