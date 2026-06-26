import os
import time
from Scripts.Util import Debug

pipelineDirectory = os.getcwd()
#sifDirectory = os.path.join(pipelineDirectory, 'SingularitySIFs')
bidsDirectory = os.path.join(pipelineDirectory, 'Data', 'AnalysisData')
outputDirectorySRC = os.path.join(pipelineDirectory, 'Output', 'src')
reconOutputDirectory = os.path.join(pipelineDirectory, 'Output', 'fib')



def RunSRC()->None:

    ## run src process using b10, b2000, b4000 for each subject
    dockerCommand = f'docker run -it --rm -v {bidsDirectory}:/BIDS -v {outputDirectorySRC}:/src -v {reconOutputDirectory}:/fib dsistudio/dsistudio:latest'

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

            niftiInDirectory = os.path.join('/BIDS', subjID, sesDir, 'dwi')
            niftisWildCard = os.path.join(niftiInDirectory, '*.nii.gz')
            absNiftiPath = os.path.join(pipelineDirectory, 'BIDS', subjID, sesDir, 'dwi')
            singleSRCOutFile = os.path.join('/src', subSesTag, f'{subjID}_{sesDir}.src.gz')

            niftiTargets = ''
            bvalTargets = ''
            bvecTargets = ''

            for file in os.listdir(absNiftiPath):
                
                if '.nii.gz' in file:

                    if niftiTargets != '':
                        niftiTargets = f'{niftiTargets},'

                    niftiTargets = f'{niftiTargets}{os.path.join(niftiInDirectory, file)}'

                elif '.bval' in file:

                    if bvalTargets != '':
                        bvalTargets = f'{bvalTargets},'

                    bvalTargets = f'{bvalTargets}{os.path.join(niftiInDirectory, file)}'

                elif '.bvec' in file:

                    if bvecTargets != '':
                        bvecTargets = f'{bvecTargets},'

                    bvecTargets = f'{bvecTargets}{os.path.join(niftiInDirectory, file)}'
            
            srcCommandPart = f'dsi_studio --action=src --source={niftisWildCard} --other_source={niftisWildCard} --output={singleSRCOutFile}'
            srcFullCommand = f'{dockerCommand} {srcCommandPart}'

            if os.path.exists(os.path.join(subSesSRCDir, f'{subjID}_{sesDir}.src.gz')):

                Debug.Log(f'{subjID}, {sesDir}: src already complete. Skipping...')

            else:

                Debug.Log(f'\nRunning DSI Studio src action for subject: {subjID}, {sesDir}.....\n')
                Debug.Log(srcFullCommand)
                os.system(srcFullCommand)
                Debug.Log(f'{subjID}, {sesDir} src exited!')



def RunREC()->None:

    dockerCommand = f'docker run -it --rm -v {bidsDirectory}:/BIDS -v {outputDirectorySRC}:/src -v {reconOutputDirectory}:/fib dsistudio/dsistudio:latest'
    
    for subSesID in os.listdir(outputDirectorySRC):

        start = time.time()
        srcInputDir = os.path.join(outputDirectorySRC, subSesID)
        recOutDirectory = os.path.join(reconOutputDirectory, subSesID) # fib/subjectsession/

        try:
            os.mkdir(recOutDirectory)
        except FileExistsError:
            Debug.Log(f'reconstruction output folder already exists for subject: {subSesID}...')
        
        srcInContents = os.listdir(srcInputDir)
        if len(srcInContents) != 1:
            Debug.Log(f'Found multiple src files where ONE was expected. Skipping {subSesID}')
            continue
        srcFileName = srcInContents[0]
        srcFileRelativePath = os.path.join('/src', subSesID, srcFileName)
        fibFileOutput = os.path.join('/fib', subSesID, f'{subSesID}_rec.icbm152_adult.qsdr.1.25.fib.gz')

        if os.path.exists(os.path.join(recOutDirectory, f'{subSesID}_rec.icbm152_adult.qsdr.1.25.fib.gz')):
            Debug.Log(f'fib output exists for {subSesID}. Skipping...')
            continue

        # find T1w image
        tokens = subSesID.split('_')
        currSub, currSes = tokens[0], tokens[1]
        currAnatDir = os.path.join(bidsDirectory, currSub, currSes, 'anat')
        otherImageAddon = ''

        for anatFile in os.listdir(currAnatDir):

            if 'T1w' not in anatFile: continue
            t1wFilePath = os.path.join('/BIDS', currSub, currSes, 'anat', anatFile)
            otherImageAddon = f' --other_image={t1wFilePath}'

        if otherImageAddon == '':

            Debug.Log(f' T1w image not found for {subSesID}, running without "--other_image" flag')

        settings = '--method=7 --param0=1.25 --template=0 --qsdr_reso=2.0' # optional settings flags
        reconCommand = f'dsi_studio --action=rec --source={srcFileRelativePath} --output={fibFileOutput} {settings}{otherImageAddon}'

        fullRecCommand = f'{dockerCommand} {reconCommand}'
        print(f'\nRunning DSI Studio recon action for subject: {subSesID}.....\n')
        print(fullRecCommand)
        os.system(fullRecCommand)

        end = time.time()
        print(f'\n{subSesID} recon exited in {end - start} seconds!\n')



def RunQAExport()->None:
    
    dockerCommand = f'docker run -it --rm -v {bidsDirectory}:/BIDS -v {reconOutputDirectory}:/fib dsistudio/dsistudio:latest'

    for subjectSession in os.listdir(reconOutputDirectory):
        thisdir = os.path.join(reconOutputDirectory, subjectSession)

        try:
            files = os.listdir(thisdir)
        except Exception as e:
            Debug.Log(f'\n{e}\n\tDirectory Empty For {subjectSession}!!!\n\tContinuing.....')
            continue
        
        qcCommandPart = ''
        for fname in files:
            if '*fib*' in fname:
                qcCommandPart = f'dsi_studio --action=exp --source=/fib/{subjectSession}/{fname} --export=qa,iso,dti_fa,ad,md '

        if qcCommandPart == '':
            Debug.Log(f'Could not find target fib file needed to construct qa extraction command.')
            continue
        
        fullCommandQC = f'{dockerCommand} {qcCommandPart}'

        # if os.path.exists(os.path.join(thisdir, 'qc.tsv')) == False:
        Debug.Log(f'{fullCommandQC}')
        os.system(fullCommandQC)