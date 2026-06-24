import os
from datetime import date

pipelineDirectory = os.getcwd()

sourceDirectoryDCM = os.path.join(pipelineDirectory, 'Data', 'InputData')
outputDirectorySRC = os.path.join(pipelineDirectory, 'Output', 'src')
outputDirectoryFIB = os.path.join(pipelineDirectory, 'Output', 'fib')
ymd = date.today().strftime('%Y-%m-%d')

def CreateDirs() -> None:
    # create directories
    for path in [sourceDirectoryDCM, outputDirectorySRC, outputDirectoryFIB]:
        try:
            os.mkdir(path)
            print(f'\nCreated directory at: {path}!')
        except FileExistsError:
            print(f'\nFile path: {path} already exists!')



def main() -> None:
    CreateDirs()
    print(f'\n\nSet-Up complete!')
    print(f'\nPlease move participant data directories to:\n     {sourceDirectoryDCM}')

if __name__ == "__main__":
    main()