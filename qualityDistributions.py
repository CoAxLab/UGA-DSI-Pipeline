import os

pipelineDirectory = os.getcwd()
figuresOutput = os.path.join(pipelineDirectory, 'Figures')
fibDirectory = os.path.join(pipelineDirectory, 'fib')
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')
singularityCommand = f'singularity exec {sifFile}'

try:
    os.mkdir(figuresOutput)
except Exception as e:
    pass

for subjectSession in os.listdir(fibDirectory):
    thisdir = os.path.join(fibDirectory, subjectSession)
    fname = os.listdir(thisdir)[0]
    fibFile = os.path.join(thisdir, fname)
    exportCommand = f'dsi_studio --action=exp --source={fibFile} --export=qa'
    
    fullCommand = f'{singularityCommand} {exportCommand}'
    print(f'{fullCommand}')
    os.system(fullCommand)