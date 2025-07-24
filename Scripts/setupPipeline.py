import os

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
sourceDirectoryDCM = os.path.join(pipelineDirectory, 'convertToBids')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
outputDirectoryFIB = os.path.join(pipelineDirectory, 'fib')

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
    os.chdir(sifDirectory)
    os.system('singularity pull docker://dsistudio/dsistudio:latest')
    os.system('singularity pull docker://nipreps/mriqc:latest')
    os.chdir(pipelineDirectory)



def main() -> None:
    CreateDirs()
    UpdateImages()
    print(f'\n\nSet-Up complete!')
    print(f'\nPlease move participant data directories to:\n     {sourceDirectoryDCM}')

if __name__ == "__main__":
    main()