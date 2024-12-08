# mii-analytics-ws2425

-- WIP --

## Description of the models and processes
create a diagram where it shows the flow of the data from source images to the resulting data from coverage and biodiversity.

this diagram should also show how the analytics accuracy and precision can be improved with new data by taking new data, 
feeding it to the system and retraining the models. 

then make the connection among the following:
- the KDD process
- the data
- the stakeholders or interested parties
- the analytics system
- etc

Present use cases of the stakeholders and how they relate to the KDD process. Something like:

- biologists:
    - take images of the field, feed to the system, and get analysis as outputs
    - then notice some flowers are being detected with low precision
    - then take more images of the flowers of interest
    - feed the new images and retrain the system

- data analists:
    - improve the system by adjusting its parameters

- other stakeholder:
    - this and that...

the overall idea is that the quality of the data is proportional to the quality of the processes that produce it, so we are interested both in the analytics process and the results.

## Under the hood

See more at [Plant diversity analysis](./plant_diversity//README.md)

See more at [Plant coverage analysis](./plant_coverage/README.md)