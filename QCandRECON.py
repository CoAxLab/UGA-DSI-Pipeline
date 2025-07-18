import os

pipelineDirectory = os.getcwd()
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
if not os.path.isdir(bidsDirectory):
    raise Exception(f'ERROR: Please run the following:\n\tsetupPipeline.py, move data to convertToBids, and run niftiToBids.py\nbefore attempting to run the pipeline!')

os.system('python runQC.py')
os.system('python addLowBToBIDS.py')
os.system('python runPipeline.py')
os.system('python qualityDistributions.py')

qcOut = os.path.join(pipelineDirectory, 'QCOutput')

if not os.path.isdir(qcOut):
    print(f'Attempting to run with "python3" command')
    os.system('python3 runQC.py')
    print(f'*****\nQC complete\n*****\nStarting lowB toggle script\n*****')
    os.system('python3 addLowBToBIDS.py')
    print(f'*****\nlowB move complete\n*****\nStarting DSI Studio pipeline\n*****')
    os.system('python3 runPipeline.py')
    print(f'*****\nDSI Studio actions complete\n*****\nStarting Quality Distributions\n*****')
    os.system('python3 qualityDistributions.py')
    print(f'*****\nQuality distributions complete!\n*****')

if not os.path.isdir(qcOut):
    raise Exception(f'ERROR: Pipeline has not run, missing dependencies or Python not on path as "python" or "python3"')