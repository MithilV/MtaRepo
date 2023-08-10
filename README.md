# MTA Data Analysis Service

## Purpose
1. The main purpose of the MtaApiCall.py file is to run a thread which keeps track of which subway lines transition from a Delay --> Non-Delay status and which subway lines transition from a Non-Delay --> Delay status
2. The /status endpoint is meant to tell the caller of the endpoint whether the subway line specified, is currently delayed or not
3. The /uptime endpoint is meant to tell the caller of the endpoint how long (seconds) a particular subway line has had a non-delayed status


## How to Run
Make sure all necessary dependencies are installed using 
```python
pip3 install __________
```
Run the file and once the code is done executing be sure to check the api_logging.log file for updates.
```python
python3 MtaApicall.py
```
