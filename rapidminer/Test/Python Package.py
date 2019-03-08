
# coding: utf-8

# In[1]:


from RM_PythonPackage.AutoModel.rm_handler import RapidMinerClient as rm
import numpy as np
from sklearn.datasets import fetch_mldata
import pandas as pd


# # Load a titanic dataset as a pandas dataframe

# In[3]:


titanic=pd.read_csv('titanic.csv')


# In[4]:


titanic


# # Connect to a Local RapidMiner Server Instance

# In[2]:


localserver=rm('http://localhost:4040','admin')


# # Save Data to the Server repo

# In[6]:


localserver.saveData(titanic,'/Python/titanicDemo')


# In[9]:


models['naive_bayes']


# # Run Automodel on the data

# In[7]:


models=localserver.auto_model(titanic,'Survived',['naive_bayes'])


# In[11]:


localserver.getJobs(models['naive_bayes']['id']).json()


# In[13]:


ss=localserver.submitService('getAutomodelData',params=[{'key':'guid','value':localserver.guid},{'key':'model','value':'naive_bayes'}])


# In[14]:


ss.json()


# # Connect to another RapidMiner Server (Partnerserver) instance

# In[15]:


partnerserver=rm('http://partnerserver.rapidminer.com:8080','rnene')


# # Get Data from RapidMiner into Python Environment

# In[16]:


dataFromProcess=partnerserver.getData('/home/rnene/Python/test/getData_5Results','process')


# In[18]:


dataFromProcess


# In[19]:


data=partnerserver.getData('/home/rnene/Python/test/Deals','data')


# In[20]:


data

