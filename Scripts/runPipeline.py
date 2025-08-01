import os
import time
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()
sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
bidsDirectory = os.path.join(pipelineDirectory, 'BIDS')
outputDirectorySRC = os.path.join(pipelineDirectory, 'src')
sifFile = os.path.join(sifDirectory, 'dsistudio_latest.sif')

singularityCommand = f'singularity exec {sifFile}'

def RunSRC()->None:
    ## run src process using b10, b2000, b4000 for each subject
    for subjID in os.listdir(bidsDirectory):
        if 'sub-' not in subjID: continue
        subBidsPath = os.path.join(bidsDirectory, subjID)

        for sesDir in os.listdir(subBidsPath):
            subSesTag = f'{subjID}_{sesDir}'
            subSesSRCDir = os.path.join(outputDirectorySRC, subSesTag)
            try:
                os.mkdir(subSesSRCDir)
            except FileExistsError:
                Debug.Log(f'src output folder already created for {subSesTag}...')
                #continue
            # source files:
            lowStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_acq-lowb_dwi.nii.gz')
            midStandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_acq-midb_dwi.nii.gz')
            highSandard = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_acq-highb_dwi.nii.gz')
            # output file:
            stdOutFile = os.path.join(subSesSRCDir, f'{subjID}_{sesDir}_dir-std.src.gz')
            srcCommandStandard = f'dsi_studio --action=src --source={lowStandard} --other_source={midStandard},{highSandard} --output={stdOutFile}'

            # reversed source files:
            lowReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-lowb_dwi.nii.gz')
            midReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-midb_dwi.nii.gz')
            highReverse = os.path.join(subBidsPath, sesDir, 'dwi' , f'{subjID}_{sesDir}_dir-rev_acq-highb_dwi.nii.gz')
            # reversed output file:
            revOutFile = os.path.join(subSesSRCDir, f'{subjID}_{sesDir}_dir-rev.src.gz')

            srcCommandReversed = f'dsi_studio --action=src --source={lowReverse} --other_source={midReverse},{highReverse} --output={revOutFile}'

            fullCommandStandard = f'{singularityCommand} {srcCommandStandard}' # appending standard command to singularity image execution command
            fullCommandReversed = f'{singularityCommand} {srcCommandReversed}' # appending reversed command to singularity image execution command
            
            skipThese = set()
            if os.path.exists(stdOutFile):
                skipThese.add(fullCommandStandard)
            if os.path.exists(revOutFile):
                skipThese.add(fullCommandReversed)

            for fullC in [fullCommandReversed, fullCommandStandard]:
                if fullC not in skipThese:
                    Debug.Log(f'\nRunning DSI Studio src action for subject: {subjID}, {sesDir}.....\n')
                    Debug.Log(fullC)
                    os.system(fullC)
                    Debug.Log(f'{subjID}, {sesDir} src exited!')
                else:
                    Debug.Log(f'{subjID}, {sesDir}: at least one src already complete. Skipping.')

reconOutputDirectory = os.path.join(pipelineDirectory, 'fib')

def RunREC()->None:
    for subSesID in os.listdir(outputDirectorySRC):
        start = time.time()
        srcInputDir = os.path.join(outputDirectorySRC, subSesID)
        recOutDirectory = os.path.join(reconOutputDirectory, subSesID) # fib/subjectsession/
        try:
            os.mkdir(recOutDirectory)
        except FileExistsError:
            Debug.Log(f'recon action already complete for subject (target output folder exists already): {subSesID}...')
        
        stdFileName, revFileName = None, None
        for file in os.listdir(srcInputDir):
            if 'rev' in file and '.sz' in file:
                revFileName = file
            elif '.sz' in file:
                stdFileName = file
        if stdFileName == None and revFileName == None:
            Debug.Log(f'ERROR: Missing an src file. Fix and re-run!')
            continue
        srcFileS = os.path.join(srcInputDir, stdFileName)
        srcFileR = os.path.join(srcInputDir, revFileName)
        fibFileOutput = os.path.join(recOutDirectory, f'{subSesID}_rec.icbm152_adult.qsdr.1.25.fib.gz')
        if os.path.exists(fibFileOutput):
            Debug.Log(f'fib output exists for {subSesID}. Skipping...')
            continue

        # find T1w image
        tokens = subSesID.split('_')
        currSub, currSes = tokens[0], tokens[1]
        currAnatDir = os.path.join(bidsDirectory, currSub, currSes, 'anat')
        otherImageAddon = ''
        for anatFile in os.listdir(currAnatDir):
            if 'T1w' not in anatFile: continue
            t1wFilePath = os.path.join(currAnatDir, anatFile)
            otherImageAddon = f' --other_image={t1wFilePath}'

        if otherImageAddon == '':
            Debug.Log(f' T1w image not found for {subSesID}, running without "--other_image" flag')

        settings = '--method=7 --param0=1.25 --template=0 --qsdr_reso=2.0' # optional settings flags
        reconCommand = f'dsi_studio --action=rec --source={srcFileS} --rev_pe={srcFileR} --output={fibFileOutput} {settings}{otherImageAddon}'

        fullRecCommand = f'{singularityCommand} {reconCommand}'
        print(f'\nRunning DSI Studio recon action for subject: {subSesID}.....\n')
        os.chdir(srcInputDir)
        print(fullRecCommand)
        os.system(fullRecCommand)
        end = time.time()
        print(f'\n{subSesID} recon exited in {end - start} seconds!\n')
        os.chdir(pipelineDirectory)