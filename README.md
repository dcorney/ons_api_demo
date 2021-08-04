# Accessing data through the ONS API

The UK's [Office of National Statistics](https://www.ons.gov.uk/) (ONS) publishes comprehensive data about the economy, population and society at national, regional and local levels. They also have an API, making (some of) the data available for directly incorporating in other tools and services. 

The ONS blog has a very nice essay on [how to access data](https://digitalblog.ons.gov.uk/2021/02/15/how-to-access-data-from-the-ons-beta-api/) using their API. There's also [their introduction and overview of the api](https://developer.ons.gov.uk/) for developers, which includes a few examples in JavaScript. However, I couldn't find any examples in Python that I could copy and paste to get going. So I created this repo... 

This repo provides a very small example of how to access the API from Python. No authentication is required, so it's pretty strightfoward. Installation is also straightforward: just clone then `pip install -r requirements.txt`. Run it using `python odi_api.py` and you should see it working.


