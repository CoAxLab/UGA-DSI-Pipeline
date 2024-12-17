import os

pipelineDirectory = os.getcwd()
dicmDirectory = os.path.join(pipelineDirectory, 'convertToBids')
outDirectory = os.path.join(pipelineDirectory, 'nifti')
configFile = os.path.join(pipelineDirectory, 'dcm2bids_config.json')

for subjID in os.listdir(dicmDirectory):
    currDicom = os.path.join(dicmDirectory, subjID)
    scafCommand = f'dcm2bids_scaffold -o {outDirectory}'
    convertCommand = f'dcm2bids -d {currDicom} -p {subjID} -s 01 -o {outDirectory} -c {configFile}'
    os.system(scafCommand)

    os.system(convertCommand)