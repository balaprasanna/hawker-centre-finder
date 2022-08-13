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

Deployed as a container in Azure Container Svc
http://hakwer-finder.ggd4g0c9fpgybxek.southeastasia.azurecontainer.io/docs#/