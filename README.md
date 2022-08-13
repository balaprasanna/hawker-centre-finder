# hawker-centre-finder

## Dataloader script
- Input: pass a local geojson dataset filepath
- Output: It will load the geojson file and parse the content, push the data into database

Datastore chosen: MongoDB
|Table schema|
| -- |
|- Name |
|- PHOTOURL|
|- ADDRESS|
|- LAT|
|- LONG|
|- S2_ZONE_{id}|


## HawkerFinder API svc

### dev
- API written in Python (FastAPI framework)


### Build
- api is build via docker
- Docker image is pushed to a public docker registry
- image: https://hub.docker.com/r/balanus/hawker-finder
- balanus/hawker-finder:latest
- To rebuild the image: `docker build -t balanus/hawker-finder .`

### Run
#### To run the image locally
- To run locally: `docker run -p 8000:80 balanus/hawker-finder:latest`
- access the api at: http://0.0.0.0:8000


### Deployment:
#### Deployed as a container in Azure Container Service
- http://hakwer-finder.ggd4g0c9fpgybxek.southeastasia.azurecontainer.io/docs#/

### Test:
- Try the different version of the find api as follows

-  ![img/step1.png](img/step1.png)
-  ![img/step2.png](img/step2.png)
-  ![img/step3.png](img/step3.png)