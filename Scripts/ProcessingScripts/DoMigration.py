import os
from Scripts.Util import Debug
from Scripts.ProcessingScripts import addLowBToBIDS

pipelineDir = os.getcwd()

MigrationMap = {
    'BIDS': os.path.join(pipelineDir, 'Data', 'AnalysisData'),
    'convertToBids': os.path.join(pipelineDir, 'Data', 'InputData'),
    'src': os.path.join(pipelineDir, 'Output', 'src'),
    'fib': os.path.join(pipelineDir, 'Output', 'fib'),
    'QCOutput': os.path.join(pipelineDir, 'Output', 'QCOutput'),
    'Figures': os.path.join(pipelineDir, 'Output'),
    'work': os.path.join(pipelineDir, 'Data', 'IntermediateData')
}



def NeedMigration()->bool:
    '''
    Checks pipeline status to determine if TIER migration is required.
    '''
    items = os.listdir(pipelineDir)
    migrationTargets = ['BIDS', 'convertToBids', 'fib', 'src', 'QCOutput', 'Figures']
    for target in migrationTargets:
        if target in items:
            return True
    return False

def DoMigration()->None:
    '''
    Performs TIER migration by moving directories.
    '''
    Debug.Log('\nPerforming TIER migration...')
    try:
        addLowBToBIDS.FlipLOWBLocation() # Moves any files from lowBFiles/ to BIDS/
    except Exception as e:
        Debug.Log(f'{e}: Not flipping lowB, no lowB to flip')
    migrationTargets = ['BIDS', 'convertToBids', 'fib', 'src', 'QCOutput', 'Figures', 'work']
    for oldDirectory in migrationTargets:
        oldPath = os.path.join(pipelineDir, oldDirectory)
        newPath = MigrationMap[oldDirectory]
        try:
            Debug.Log(f'mv {oldPath} {newPath}', True)
            os.system(f'mv {oldPath} {newPath}')
        except NotADirectoryError:
            Debug.Log(f'\nNo directory at: {oldPath}', True)
        except FileExistsError:
            Debug.Log(f'\nFile path: {newPath} already exists!', True)

def CheckAndMigrate() -> None:
    if NeedMigration():
        DoMigration()
    print('\nTIER migration complete!')
    print('Please check the BIDS directory for migrated files.')

if __name__ == '__main__':
    CheckAndMigrate()