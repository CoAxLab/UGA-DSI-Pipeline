import os

pipelineDirectory = os.getcwd()
dicmDirectory = os.path.join(pipelineDirectory, 'convertToBids')
preOutDirectory = os.path.join(pipelineDirectory, 'bids')
try:
    os.mkdir(preOutDirectory)
except Exception as e:
    print(f'e\nmoving on...\n')
configFile = os.path.join(pipelineDirectory, 'dcm2bids_config.json')

for subjID in os.listdir(dicmDirectory):
    outDirectory = os.path.join(preOutDirectory, subjID)
    currDicom = os.path.join(dicmDirectory, subjID)
    scafCommand = f'dcm2bids_scaffold -o {outDirectory}'
    convertCommand = f'dcm2bids -d {currDicom} -p {subjID} -o {outDirectory} -c {configFile}'
    os.system(scafCommand)

    os.system(convertCommand)
