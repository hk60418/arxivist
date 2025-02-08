# ArXiv Agent
Local agent for making staying up to data with research published in ArXiv.

## Installation and setup

### Setup python, environment, and packages

This app was developed on python 3.12. So, presumably safest way to run the application is to set app to use python 3.12
, create a virtual environment, install packages from requirement.txt, and install app packages (with "pip install -e ." 
in the repository root).

### Setup Qdrant vector storage

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

### Before running any components: Set up your environment
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
- set the environment

### Arxiv_agent usage

\# imports\
from arxiv_parser import ArxivParser\
from datetime import datetime, timedelta

parser = ArxivParser()

\# Get papers from a specific date and category\
papers = parser.get_daily_papers(datetime.now() - timedelta(days=1), 'cs.AI')

\# Download and save papers\
parser.save_papers(papers, 'output_directory')

## Tests
Run tests in directory root with:
``` bash
pytest
```