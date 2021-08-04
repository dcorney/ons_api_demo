# Accessing data through the ONS API

The UK's [Office of National Statistics](https://www.ons.gov.uk/) (ONS) publishes comprehensive data about the economy, population and society at national, regional and local levels. They also have an API, making (some of) the data available for directly incorporating in other tools and services. 

The ONS blog has a very nice essay on [how to access data](https://digitalblog.ons.gov.uk/2021/02/15/how-to-access-data-from-the-ons-beta-api/) using their API. There's also [their introduction and overview of the api](https://developer.ons.gov.uk/) for developers, which includes a few examples in JavaScript. However, I couldn't find any examples in Python that I could copy and paste to get going. So I created this repo... 

This repo provides a very small example of how to access the API from Python. No authentication is required, so it's pretty strightfoward. Installation is also straightforward: just clone then `pip install -r requirements.txt`. Run it using `python odi_api.py` and you should see it working.

## Terminology

"Dimensions" refers to particular slices of a dataset. For example, inflation figures might be available for the UK, England, Wales, Scotland and Northern Ireland. So the geography dimension could be set to any one of those in order to retrieve all the data from one location. In the code here, the "time" dimension is forced to the wildcard "\*" as I want to get a whole time-series for a dataset; if you fixed the time dimension and set geography to "\*", then it would return the value for each region at the specified time.

The `get_dimensions()` function returns a stucture listing all the valid values for each dimension of a dataset. A subset of these must then be specified and passed into the `get_observations()` function to actually retrieve the data.