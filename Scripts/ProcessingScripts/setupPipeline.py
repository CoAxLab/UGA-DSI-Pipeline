import os
from datetime import date

pipelineDirectory = os.getcwd()

allSetupPaths = []


allSetupPaths.append(os.path.join(pipelineDirectory, 'Data'))
allSetupPaths.append(os.path.join(pipelineDirectory, 'Output'))
sourceDirectoryDCM = os.path.join(pipelineDirectory, 'Data', 'InputData')
allSetupPaths.append(sourceDirectoryDCM)
allSetupPaths.append(os.path.join(pipelineDirectory, 'Data', 'IntermediateData'))
allSetupPaths.append(os.path.join(pipelineDirectory, 'Data', 'AnalysisData'))
allSetupPaths.append(os.path.join(pipelineDirectory, 'Output', 'src'))
allSetupPaths.append(os.path.join(pipelineDirectory, 'Output', 'fib'))
allSetupPaths.append(os.path.join(pipelineDirectory, 'Output', 'Figures'))
ymd = date.today().strftime('%Y-%m-%d')

def CreateDirs() -> None:
    # create directories
    for path in allSetupPaths:
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