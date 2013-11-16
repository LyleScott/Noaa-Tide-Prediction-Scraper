NoaaTidePredictionScraper
=========================

A scraper I wrote to get the tide prediction information from NOAA. For reasons.

Workflow:
* scrape the [NOAA prediction pages](http://tidesandcurrents.noaa.gov/tide_predictions.html) for URLs to all the stations
    * builds a nicely formatted XML tree of the stations an dtheir locations...
      this is a byproduct of needing to have this file for something I was
      working on.
* go to each station's page and download the yearly preidction files
* output parsed data into something meaningful


NOAA Tide Predictions: http://tidesandcurrents.noaa.gov/tide_predictions.html
