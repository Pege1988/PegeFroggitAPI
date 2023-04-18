# PegeFroggitAPI
Script to fetch weather data from Pege Froggit Weather station using ecowitt API.

## Description
The app consists of a main script executing the functions defined in the main module.

Main steps in app:
1. Fetch access token from Ecowitt using API containing personal app_id and secret code
2. Fetch JSOn file containing Pege Froggit weather data using API containing access token and personal open ID
3. Extract various variables from JSON file
4. Store data values in SQLite database

## TO DO
- Add unit tests

## Installation notes
Working directory is identified in script to distinguish between TEST and PROD environment (i.e. local vs network (SYNOLOGY)). 
Once dev and tests finished, store updated/new file(s) and folder(s) on Synology NAS.
For integration testing purposes, run script manually on Synology and check results.

## Information on Ecowitt API
Documentation on API: https://doc.ecowitt.net/web/#/1?page_id=11
Device developer information: https://api.ecowitt.net/index/user/mydevice.html


