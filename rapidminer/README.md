# rapidminer Module

This module provides the RapidMinerClient and AutoModelClient submodules.

## RapidMinerClient Module

This module connects to the RapidMiner Server using the credentials provided by the user. Once connected it provides a set of utility functions to perform various tasks such as:

* Installing RapidMiner processes, services to the server
* Retrieve RapidMiner processes from the server
* Submit jobs to the RapidMiner server
* Retrieve a job from the RapidMiner server
* Retrieve status of all the Jobs on the RapidMiner Server
* Retrieve data from a RapidMiner repository/process
* Save data to a RapidMiner repository
* Submit a RapidMiner process as a REST service
* Retrieve the queues present on the RapidMiner server

## AutoModelClient Module (Beta Version)

This module connects to the RapidMiner AutoModel and builds predictive models(Logistic Regression, Decision trees, Naive Bayes, Generalized Linear Models) based on the data passed to the autoModel function.
