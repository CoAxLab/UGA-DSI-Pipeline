import os
from datetime import date

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryDCM = os.path.join(pipelineDirectory, 'convertToBids')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
outputDirectoryFIB = os.path.join(pipelineDirectory, 'fib')
ymd = date.today().strftime('%Y-%m-%d')

def CreateDirs() -> None:
    # create directories
    for path in [sifDirectory, sourceDirectoryDCM, outputDirectorySRC, outputDirectoryFIB]:
        try:
            os.mkdir(path)
            print(f'\nCreated directory at: {path}!')
        except FileExistsError:
            print(f'\nFile path: {path} already exists!')

def UpdateImages() -> None:
    # pull SIF file for dsi studio
    #os.chdir(sifDirectory)
    dsiName = os.path.join(sifDirectory, f'dsistudio_{ymd}')
    qcName = os.path.join(sifDirectory, f'mriqc_{ymd}')
    os.system(f'singularity pull --name {dsiName} docker://dsistudio/dsistudio:latest --disable-cache')
    os.system(f'singularity pull --name {qcName} docker://nipreps/mriqc: --disable-cache')
    #os.chdir(pipelineDirectory)



def main() -> None:
    CreateDirs()
    UpdateImages()
    print(f'\n\nSet-Up complete!')
    print(f'\nPlease move participant data directories to:\n     {sourceDirectoryDCM}')

if __name__ == "__main__":
    main()