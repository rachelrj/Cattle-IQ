# CattleIQ

CattleIQ is a python application which scrapes cattle market reports and stores these records in both AWS S3 and in NOT DECIDED DATABASE.

This application is ran regularly via AWS eventbridge to scrape new data.

This application is Dockerized in order to be stored in ECR and ran as a ECS task in AWS. It is also Dockerized for portability.

# Table of Contents

1. [Architecture](#architecture)
2. [Requirements](#requirements)
3. [Running](#running)
4. [FAQ](#faq)
5. [Maintainers](#maintainers)
6. [Contacts](#contacts)

# Architecture

There are three applications which make up the Docker container.

## The app

Contains all the python code. It utilizes the other containers in order to use Selenium.

The entry point is index.py, which creates the driver and runs all the scrapes in the scripts folder.

## Selenium-hub

The hub is the central point wherein the scrapes are loaded.

## Firefox node

The firefox node will execute the scrapes that have been loaded onto the hub.

# Requirements

## Python

[Install python](https://www.python.org/downloads/)

## Docker

[Install Docker] (https://docs.docker.com/get-docker/)

## AWS

Save your [Credentials] (https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) in your local config file. Ask team for access if needed.

# Running

To run locally within your docker container, point your hub_url to "http://selenium_hub:4444/wd/hub". Do this in index.py. There should be commented out code and instructions for how to do so.

In your terminal run `docker-compose up`

Please note that running in the docker container locally WILL NOT update AWS records because the docker container does not contain AWS credentials. This repository is not meant to update or write records locally. It is meant only to update and write records on the cloud.

# FAQ

Where is the AWS task defined? If you are logged into AWS, go to: https://us-east-1.console.aws.amazon.com/ecs/v2/task-definitions/cattleiq-task?region=us-east-1

Does the application halt upon encountering an error? No, the try except blocks are meant to catch, report, and move on from errors.

How are errors handled? Currently errors are emailed to the maintainers. The email helper function is located in the helpers directory.

Is there any logging within the application? The print statements are logged to AWS Cloudwatch. More in depth logging is intended for the future.

# Maintainers

Rachel Joyce - rachel@cattleiq.com
Shane Joyce - shane@cattleiq.com

# Contacts

Matt McDowell - matt@cattleiq.com
Chris Provost - chris@cattleiq.com
