# Plan and What do we want to achieve with this?
- Ingestion
  - fetch daily
  - store into MongoDB
    - create vector indexes
      - for abstract
      - for text
  - store LLM context for fast access
- Usage
  - Ask about new experiments and results since last check?
  - 

# Installation and setup

## Setup python, environment, and packages

This app was developed on python 3.12. So, presumably safest way to run the application is to set app to use python 3.12
(for example with pyenv), create a virtual environment, install packages from requirement.txt, and install app packages
(with pip install -e . in the repository root).

## Setup MongoDB Atlas
MongoDB Atlas provides mongodb with vector indexing and search, with local deployments.

Excercise setup is here: https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/vector-search-quick-start/

Installing MongoDB Atlas and creating a local deployment for the app:
- Install Atlas CLI
- Install Docker
- Create Atlas account with cmd: "atlas setup"
- Create a local deployment with cmd: "atlas deployments setup", preferrably with fixed port number so that the 
connection string can remain constant in the app configuration

## Setup Qdrant vector storage

Qdrant is the application database and vector storage. Article data is stored in the Qdrant entry payloads.

Source for the setup exersice is here: https://qdrant.tech/documentation/quickstart/

1. Pull docker image
```bash
docker pull qdrant/qdrant
```
2. Run the service
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```
3. Install the python client
```bash
pip install qdrant_client
```

## Before running any components: Set up your environment
1. Activate you virtual environment.
2. App configuration is based on your environment variable. It suffices to use the same as me during development:
``` bash
export APP_NAME=arxiv_parser
export ENV=dev
```
You can use whatever you choose but then you must adapt configuration to that.
3. Start your database deployment
- start docker
- run the container with your deployment
- set the environemnt

Creating database and collection for the app:

## Initialise Database
```bash
python src/database/setup.py
```

# Arxiv_agent usage

\# imports\
from arxiv_parser import ArxivParser\
from datetime import datetime, timedelta

parser = ArxivParser()

\# Get papers from a specific date and category\
papers = parser.get_daily_papers(datetime.now() - timedelta(days=1), 'cs.AI')

\# Download and save papers\
parser.save_papers(papers, 'output_directory')

# MongoDB Atlas
