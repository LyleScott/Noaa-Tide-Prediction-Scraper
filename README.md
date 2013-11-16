NOAA Tide Prediction Scraper
============================

A scraper I wrote to get the tide prediction information from NOAA. For reasons.

Workflow:
* scrape the [NOAA prediction pages](http://tidesandcurrents.noaa.gov/tide_predictions.html) for URLs to all the stations
    * builds a nicely formatted XML tree of the stations and their locations...
      this is a byproduct of needing to have this file for something I was
      working on.
    * stored in stations.xml 
* go to each station's page and download the yearly prediction files
    * downloaded to xml/* for each station.


Outputting the station info to XML is mainly to provide a proof-of-concept.
I kept it simple since database abstraction is out of the scope of what I was
trying to provide.


NOAA Tide Predictions: http://tidesandcurrents.noaa.gov/tide_predictions.html
