import os

pipelineDirectory = os.getcwd()
figuresOutput = os.path.join(pipelineDirectory, 'Figures')
fibDirectory = os.path.join(pipelineDirectory, 'fib')

try:
    os.mkdir(figuresOutput)
except Exception as e:
    pass

for subjectSession in os.listdir(fibDirectory):
    
    
    
    
    pass