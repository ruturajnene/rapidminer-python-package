import requests
import numpy as np
import pandas as pd
import webbrowser

class AutoModelClient():

    def __init__(self):
        self.models=['LOGREG','NAIVE_BAYES','GLM','DECISION_TREE']
        self.idToken='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IlJFRkZOVGMyTWtWR1FUWkdPVVpHUlRRNE1EazRNVFU1UVRsRFF6bENSRVJGUlRaQk1EbEROdyJ9.eyJuaWNrbmFtZSI6InJuZW5lIiwibmFtZSI6InJuZW5lQHJhcGlkbWluZXIuY29tIiwicGljdHVyZSI6Imh0dHBzOi8vcy5ncmF2YXRhci5jb20vYXZhdGFyL2FiYzNhZGY1ZWRmNWE3NTVjYTYwZDY3ZDU4NmZhYWRmP3M9NDgwJnI9cGcmZD1odHRwcyUzQSUyRiUyRmNkbi5hdXRoMC5jb20lMkZhdmF0YXJzJTJGcm4ucG5nIiwidXBkYXRlZF9hdCI6IjIwMTgtMTAtMDJUMTE6MDc6NTkuMzI2WiIsImVtYWlsIjoicm5lbmVAcmFwaWRtaW5lci5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hdXRoLXRlc3QucmFwaWRtaW5lci5jb20vIiwic3ViIjoiYXV0aDB8NWIzYmEwMGI0NGFlNGEyNTIwZmVjMzg1IiwiYXVkIjoiZmFyVURaak8wM3owQ0Z6RFg2MnIzSG1jeFE0Nmk3RGMiLCJpYXQiOjE1Mzg0ODA4MDIsImV4cCI6MTUzODUxNjgwMiwiYXRfaGFzaCI6IjhRUGRlQXhKdlozY1BvWUhJLWpXU0EiLCJub25jZSI6Ill0TTkzbUVGNGRpVX5sLXlUSnI4WEFCSzRaZVZESHdtIn0.DM6jrjc7T7649NZ18WaSUMZUO4Gy3B23z0L_Cx-CGpbzRVJWk1btS8g1XjGmfhiK58eqKdV52IcyWM1zIP0lPUclx513NKfAsrBqlXs6KJ2LWKj0DQJ9hp6dM2WC5NkVJLPGtzxb7IOpuxOGn-LeGyaUI2iXkXP3wGLfGVDxtjILXwSt5XO7iq6TnoQEZx5zGisZfSucXZkmatTZZAQ0yAxpq9QDfChq1ZXDaOBeqD4EVGln3uuQSx42HsBX6fLijUVnMINVAFwiwScd6v8W4wB8TzIxZO9O2QOBTs-1InxWASJLpXo5UFNGp2sZnDHGpx8YtG_raLtgks-6yz34TA'
        print('Connected to AutoModelClient')

    def autoModel(self,data,label,models=None):
        if models is None:
            models=['LOGREG','NAIVE_BAYES','GLM','DECISION_TREE']

        files={'file': ('data.csv',data.to_csv(index=False))}
        url='http://localhost:3000'
        headers = { 'Authorization' : 'Bearer %s' %  self.idToken}
        # API Call for post Data
        postData=requests.post(url=url+'/api/data',files=files,headers=headers)
        dataResponse=postData.json()
        # print(dataResponse)

        # API call to post modeling task
        modelingTaskData={'dataId':dataResponse['id'],'type':'new'}
        headers['Content-Type']='application/json'
        postModelingTask=requests.post(url=url+'/api/modelingtasks',json=modelingTaskData,headers=headers)
        modelingTaskResponse=postModelingTask.json()

        # API call to post label
        postLabel=requests.post(url=url+'/api/modelingtasks/'+modelingTaskResponse['id']+'/label',json={'attributeName':label},headers=headers)
        labelResponse=postLabel.json()

        modelInputs=[]
        for inputs in labelResponse['modelInputs']:
            if(inputs['modelAttributeStatistics']['status']=='GREEN'):
                modelInputs.append({'attributeName':inputs['attributeName']})

        # API call to post model inputs
        postModelInputs=requests.post(url=url+'/api/modelingtasks/'+modelingTaskResponse['id']+'/modelinputs',json=modelInputs,headers=headers)
        modelInputsResponse=postModelInputs.json()

        modelsBody=list(map(lambda model: {'type':model,'selected':True} if model in models else {'type':model,'selected':False},self.models))
        
        # API call to post models
        for model in modelsBody:
            postModels=requests.post(url=url+'/api/modelingtasks/'+modelingTaskResponse['id']+'/models',json=model,headers=headers)
            modelsResponse=postModels.json()
        
        # API call to post execution
        postExecutions=requests.post(url=url+'/api/executions',json={'modelingTaskId':modelingTaskResponse['id']},headers=headers)
        executionsResponse=postExecutions.json()

        resultsURL= 'http://localhost:3000/predictions/'+modelingTaskResponse['id']+'/results'
        webbrowser.open_new_tab(resultsURL)


        # API call to check if execution complete
        while self.__isExecutionFinished(executionsResponse)!=True:
            # API call to get execution results
            getExecutions=requests.get(url=url+'/api/executions?mti='+modelingTaskResponse['id'],headers=headers)
            executionsResponse=getExecutions.json()

        return resultsURL

    def __isModelExecutionFinished(self,model):
        return model['state'] == 'FINISHED' or model['state'] == 'ERROR' or model['state'] == 'CANCELLED'

    def __isExecutionFinished(self,models):
        return all(map(self.__isModelExecutionFinished,models))

    def dataUpload(self,data):
        files={'file': ('data.csv',data.to_csv(index=False))}
        url='http://localhost:3000'
        headers = { 'Authorization' : 'Bearer %s' %  self.idToken}
        # API Call for post Data
        postData=requests.post(url=url+'/api/data',files=files,headers=headers)
        dataResponse=postData.json()
        # print(dataResponse)

        # API call to post modeling task
        modelingTaskData={'dataId':dataResponse['id'],'type':'new'}
        headers['Content-Type']='application/json'
        postModelingTask=requests.post(url=url+'/api/modelingtasks',json=modelingTaskData,headers=headers)
        modelingTaskResponse=postModelingTask.json()

        dataUploadURL= 'http://localhost:3000/predictions/'+modelingTaskResponse['id']+'/target'
        webbrowser.open_new_tab(dataUploadURL)

        return dataUploadURL