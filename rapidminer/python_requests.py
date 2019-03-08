import requests
import numpy as np
import csv
import base64
import jwt
import pandas as pd
import xml.etree.ElementTree as et
import pickle
import os

class RapidMinerClient():
    
    def __init__(self,url,username,password):

        print(os.path.dirname(os.path.abspath(__file__)))
        # URL of the Rapidminer Server
        self.server_url=url
        # RapidMiner Server Username 
        self.username=username
        # RapidMiner Server Password
        self.password=password

        # Connect to the RM Server
        self.__connect()

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
                mydict[key]=row[i]
            return mydict

        exampleSet=list(map(lambda row: createDict(row) ,data.values))
        return exampleSet

    # path - path to the process/dataset on the repository
    # type - type of the fetch i.e through a process or dataset  
    def getData(self,path,dataType):
        if(dataType=="process"):
            numeric=1
        elif dataType== "data":
            numeric=2
        try:
            r=requests.post(self.server_url+"/api/rest/process/getData?",json={"path":path,"type":numeric},headers=self.auth_header)
            response=r.json()
            if(dataType=='process'):
                datasets=[pd.DataFrame(np.array([list(row.values()) for row in dataset]),columns=list(dataset[0].keys())) for dataset in response]
            else:
                datasets=pd.DataFrame(np.array([list(row.values()) for row in response]),columns=list(response[0].keys()))
            return datasets
        except Exception as e:
            print("Connection lost, reconnect to the Server ",e)

    def reconnect(self):
        self.__connect()


    # jobId= The jobId for a particular job
    def getJobs(self,jobId=None):
        if jobId==None:
            URL=self.server_url+"/executions/jobs"
        else:
            URL=self.server_url+"/executions/jobs/"+jobId
        print(URL)
        r=requests.get(URL,headers=self.auth_header)
        print(r.status_code)
        response=r.json()
        return response

    def getQueues(self):
        URL=self.server_url+"/executions/queues?"
        print(URL)
        r=requests.get(URL,headers=self.auth_header)
        print(r.status_code)
        response=r.json()
        return response

    def getProcess(self,path):
        URL=self.server_url+"/api/rest/resources"+path
        print(URL)
        r=requests.get(URL,headers=self.auth_header)
        print(r.status_code)
        # response=r.json()
        return r.text

# http://partnersrv.rapidminer.com:8080/api/rest/
    def getModel(self):
        URL=self.server_url+"/api/rest/process/Python%20Model?"
        print(URL)
        local_filename = 'pymodel.pickle'
        # NOTE the stream=True parameter
        r = requests.get(URL, stream=True,headers=self.auth_header)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        # r=requests.get(URL,headers=self.auth_header)
        print(r.status_code)
        with open(local_filename, 'rb') as handle:
            var = pickle.load(handle)
        # response=r.json()
        return var

    def postProcess(self,path,process):
        URL=self.server_url+"/api/rest/resources"+path
        print(URL)
        head=self.auth_header.copy()
        head['Content-Type']='application/vnd.rapidminer.rmp+xml'
        r=requests.post(URL,headers=head,data=process)
        print(r.status_code)
        # response=r.json()
        return r

    # queueName - The name of the queue the process should be run on
    # processPath - The path of the process on the server to be encoded into base64 format
    # location - The location of the process
    def createJob(self,queueName,processPath,location):

        URL=self.server_url+"/executions/jobs?"
        
        # convert process XML file to a string
        # processXML=et.parse(processPath)
        # process=et.tostring(processXML.getroot(),encoding='utf8',method='xml').decode('ascii')

        process=self.getProcess(processPath)
        body={"queueName":queueName,"process":base64.b64encode(bytes(process,'utf-8')).decode("ascii"),"location":location}
        r=requests.post(url=URL,json=body,headers=self.auth_header)
        print(r.status_code)
        response=r.json()
        return response

        # def autocleanse(self,datapath)
        # String s = xmlfrompackage;
        # newxML = s.replace(__path,datapath)
        
    # # helper method(private)
    # def __readCSV(self):
    #     # File path to the local CSV Dataset
    #     self.csv.seek(0)
    #     cfil=csv.reader(self.csv)
    #     data=np.vstack([np.array(line) for line in cfil])
    #     return data

    def decisionTree(self,data,dataType,label):

        if(dataType==1):
            r=requests.post(self.server_url+"/api/rest/process/decisionTreeModel?type="+str(dataType)+"&label="+label,json={"data":data},headers=self.auth_header)
        else:
            exampleSet=self.__dataFrameToExampleSet(data)
            r=requests.post(self.server_url+"/api/rest/process/decisionTreeModel?type="+str(dataType)+"&label="+label,json=exampleSet,headers=self.auth_header)
        response=r.json()
        return response
    # def getPredictions(self,path,label):

    #     self.csv=open(path)
    #     # Input Exampletable 
    #     self.exampleTable=self.__readCSV()
    #     # Input attributes
    #     self.attributes=self.exampleTable[0]
    #     self.exampleTable=self.exampleTable[1:]

    #     def createDict(row):
    #         mydict={}
    #         for i,key in enumerate(self.attributes):
    #             mydict[key]=row[i]
    #         return mydict
        
    #     jsonRequest=[createDict(row) for row in self.exampleTable]
    #     URL=self.server_url+"/api/rest/process/post_data?label="+ label

    #     # files={'file': open('titanic.csv')}

    #     try:
    #         r=requests.post(url=URL,json=jsonRequest,headers=self.auth_header)

    #         jsonBody=r.json()

    #         attributes=np.array(list(jsonBody[0].keys()))
    #         outputTable=np.array([list(row.values()) for row in jsonBody])
    #         pLabel='prediction('+label+')'
    #         predicted_label=np.array([row[pLabel] for row in jsonBody])

    #     except Exception as e:
    #         print("Connection lost,Reconnect to the Server ", e)
    #     else:
    #         return jsonBody,outputTable,attributes

    def submitRandomJob(self,queueName,processPath,row,column):

        URL=self.server_url+"/executions/jobs?"
        # convert process XML file to a string
        # processXML=et.parse('C:\\Users\\RuturajNene\\Documents\\RM_PythonPackage\\myprocess.xml')
        # process=et.tostring(processXML.getroot(),encoding='utf8',method='xml').decode('ascii')
        processXML=open('C://Users//RuturajNene//Documents//RM_PythonPackage//myprocess.xml')
        process=processXML.read()
        x=self.postProcess(processPath+'/process/finalProcess',process)
        print(x)
        if(x.status_code ==201):
            process=self.getProcess(processPath+'/process/finalProcess')
            process=process.replace('MYROW',str(row))
            process=process.replace('MYCOLUMN',str(column))
            process=process.replace('MYPATH',processPath+'/data/sampleOut')
            body={"queueName":queueName,"process":base64.b64encode(bytes(process,'utf-8')).decode("ascii"),"location":processPath+'/process/finalProcess'}
            r=requests.post(url=URL,json=body,headers=self.auth_header)
            print(r.status_code)
            response=r.json()
            return response
        else:
            return "Failed"