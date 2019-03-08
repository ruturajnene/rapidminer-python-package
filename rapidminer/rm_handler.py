import requests
import numpy as np
import base64
import jwt
import pandas as pd
import pickle
import os
import getpass
from functools import reduce
import uuid

class RapidMinerClient():
    """docstring for RapidMinerClient"""
    def __init__(self,url,username):
    # URL of the Rapidminer Server
        self.server_url=url
        # RapidMiner Server Username
        self.username=username
        # RapidMiner Server Password
        self.password= getpass.getpass(prompt='Password: ')
        
        # Connect to the RM Server
        self.__connect()

        self.__package_path=os.path.dirname(os.path.abspath(__file__))

    # helper method to save process in the RapidMiner Repo(private)
    def __installRapidMinerProcess(self,fileName):
        file=open(self.__package_path+'\\'+fileName+'.xml')
        process=file.read()
        x=self.postProcess('/Python/process/'+fileName,process)
        file.close()
        # print(x.status_code)

    def __installRapidMinerServices(self,fileName):
        file=open(self.__package_path+'\\'+fileName+'.xml')
        descriptor=file.read()
        x=self.postService(fileName[:-10],descriptor)
        file.close()
        
    # helper method(private)
    def __connect(self):
        # Encode the basic Authorization header
        userAndPass = base64.b64encode(bytes(self.username+":"+self.password, 'utf-8')).decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }

        r=requests.get(url=self.server_url+'/internal/jaxrest/tokenservice',headers=headers)
        
        # JWT idToken for the RM Server
        self.idToken=r.json()['idToken']

        # Bearer Authorization header
        self.auth_header = { 'Authorization' : 'Bearer %s' %  self.idToken }
        
        # RM Server Client Info
        self.tokenDecoded=jwt.decode(r.json()['idToken'],verify=False)
        if(r.status_code==200):
            print("Successfully connected to the Server")
        else:
            print("Connection Error")

    def __dataFrameToExampleSet(self,data):
        attributes=list(data.columns)
        
        def createDict(row):
            mydict={}
            for i,key in enumerate(attributes):
                mydict[key]=str(row[i])
            return mydict

        exampleSet=list(map(lambda row: createDict(row) ,data.values))
        return exampleSet

    def installPackage(self):

        # install process on the server repo
        for filename in os.listdir(self.__package_path):
            if not filename.endswith('.xml'): continue

            if 'Descriptor' not in filename:
                self.__installRapidMinerProcess(filename[:-4])
            else:
                self.__installRapidMinerServices(filename[:-4])

    # path - path to the process/dataset on the repository
    # type - type of the fetch i.e through a process or dataset  
    def getData(self,path,dataType):
        if(dataType=="process"):
            numeric=1
        elif dataType== "data":
            numeric=2
        try:
            r=requests.post(self.server_url+"/api/rest/process/pythonGetData?",json={"path":path,"type":numeric},headers=self.auth_header)
            response=r.json()
            if(dataType=='process'):
                datasets=[pd.DataFrame(np.array([list(row.values()) for row in dataset]),columns=list(dataset[0].keys())) for dataset in response]
            else:
                datasets=pd.DataFrame(np.array([list(row.values()) for row in response]),columns=list(response[0].keys()))
            return datasets
        except Exception as e:
            print("Connection lost, reconnect to the Server ",e)

    def saveData(self,data,path):
        params=[{'key':'path','value':path},{'key':'sample','value':'15'}]
        response=self.submitService('pythonSaveData',data,params)
        # print(response.json())
        if response.status_code==200:
            print('Data saved Successfully')
        else:
            print('Error while saving data')

    # jobId= The jobId for a particular job
    def getJobs(self,jobId=None):
        if jobId==None:
            URL=self.server_url+"/executions/jobs"
        else:
            URL=self.server_url+"/executions/jobs/"+jobId
        # print(URL)
        r=requests.get(URL,headers=self.auth_header)
        # print(r.status_code)
        # response=r.json()

        # returns a JSON object tha has details for the particular job id or an array of Jobs with details under the content tag
        # return response

        return r

    def getQueues(self):
        URL=self.server_url+"/executions/queues?"
        print(URL)
        r=requests.get(URL,headers=self.auth_header)
        print(r.status_code)
        # response=r.json()

        # returns a JSON array of objects representing each queue withs it's properties
        # return response

        return r

    # method for getting the process XML
    def getProcessXML(self,path):
        URL=self.server_url+"/api/rest/resources"+path
        # print(URL)
        r=requests.get(URL,headers=self.auth_header)
        # print(r.status_code)
        # response=r.json()

        # returns the process XML as a string
        return r.text


    # method to submit job with raw XML
    # queueName - The name of the queue the process should be run on
    # processPath - The path of the process on the server to be encoded into base64 format
    # location - The location of the process
    def submitJobXML(self,queueName,process,location):

        URL=self.server_url+"/executions/jobs?"
        
        # convert process XML file to a string
        # processXML=et.parse(processPath)
        # process=et.tostring(processXML.getroot(),encoding='utf8',method='xml').decode('ascii')

        body={"queueName":queueName,"process":base64.b64encode(bytes(process,'utf-8')).decode("ascii"),"location":location}
        r=requests.post(url=URL,json=body,headers=self.auth_header)
        # print(r.status_code)
        return r

    #   method to submit job with with reference to process path on server
    def submitJob(self,queueName,processPath,params,location):
        processXML=self.getProcessXML(processPath)
        for param in params:
            processXML=processXML.replace(param['key'],param['value'])
        r=self.submitJobXML(queueName,processXML,location)
        return r

    #  method for submitting web services
    def submitService(self,serviceName,data=None,params=None):

        if data is None:
            body=[]
        else:
            body=self.__dataFrameToExampleSet(data)
        if params!=None:
            url=reduce(lambda final,param: final+param['key']+'='+param['value']+'&',params,'')
        else:
            url=''
        url=self.server_url+'/api/rest/process/'+serviceName+'?'+url
        r=requests.post(url=url,json=body,headers=self.auth_header)

        return r

    # method to save the process on the repo from the xml
    def postProcess(self,path,process):
        URL=self.server_url+"/api/rest/resources"+path
        # print(URL)
        head=self.auth_header.copy()
        head['Content-Type']='application/vnd.rapidminer.rmp+xml'
        r=requests.post(URL,headers=head,data=process)
        # print(r.status_code)
        # response=r.json()

        # returns the status message
        return r

    def postService(self,serviceName,descriptor):
        URL=self.server_url+"/api/rest/service/"+serviceName
        # print(URL)
        r=requests.post(URL,auth=(self.username,self.password),data=descriptor)
        # print(r.status_code)
        # response=r.json()

        # returns the status message
        return r

    def auto_model(self,data,label,models:list):

        self.guid=str(uuid.uuid4())
        self.saveData(data,'/Python/Data/'+self.guid+'/'+self.guid)
        params=[{'key':'%{guid}','value':self.guid},{'key': '%{label}', 'value': label}]
        response={}
        for model in models:
            r=self.submitJob('DEFAULT','/Python/process/'+model,params,'/Python/Data/'+self.guid+'/'+model+'/process')
            # print(r)
            response[model]=r.json()
        return response
