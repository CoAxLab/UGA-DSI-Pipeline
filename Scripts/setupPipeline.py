import os

pipelineDirectory = os.getcwd()

# create directories
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryDCM = os.path.join(pipelineDirectory, 'convertToBids')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
outputDirectoryFIB = os.path.join(pipelineDirectory, 'fib')
for path in [sifDirectory, sourceDirectoryDCM, outputDirectorySRC, outputDirectoryFIB]:
    try:
        os.mkdir(path)
        print(f'\nCreated directory at: {path}!')
    except FileExistsError:
        print(f'\nFile path: {path} already exists!')

# pull SIF file for dsi studio
os.chdir(sifDirectory)
os.system('singularity pull docker://dsistudio/dsistudio:latest')
os.system('singularity pull docker://nipreps/mriqc:latest')
os.chdir(pipelineDirectory)

print(f'\n\nSet-Up complete!')
print(f'\nPlease move participant data directories to:\n     {sourceDirectoryDCM}')