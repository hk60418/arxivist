# ArXiv Agent
Local agent for staying up to date with research published in ArXiv.

## Installation and setup

### Setup python, environment, and packages

This app was developed on python 3.12. So, presumably safest way to run the application is to set app to use python 3.12
, create a virtual environment, install packages from requirement.txt, and install app packages (with "pip install -e ." 
in the repository root).

### Setup Qdrant vector storage

Qdrant is the application database/vector storage. Article data is stored in the Qdrant entry payloads.

The instructions for the setup exercise below were taken from here: https://qdrant.tech/documentation/quickstart/

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
2. Install requirements & this package.
```bash
pip install -r requirements.txt
pip install -e .
```
2. App configuration is based on your environment variable. It might suffice to use the same configuration that I used 
during development:
``` bash
export APP_NAME=arxiv_parser
export ENV=dev
```
You can use whatever you decide to use but then you must adapt your configuration for that.
3. Start your database deployment
- start docker
- run the container that hosts your Qdrant deployment
- set the environment

### ArXivist usage

#### Getting articles

Before starting user activities with the ArXivist you need to get some articles. Set up the DB collection name, 
categories that you are interested in, and local file system directory for the article registry. These can be set in the 
configuration file config/<APP_NAME>.yml.

After setting these up it makes sense to do a batch import, importing all the articles in the chosen categories that has
been published since chosen date. You can do this with scripts/import_articles_since_date.py:

```bash
# usage format:
python scripts/import_articles_since_date.py <YYYY-MM-DD>

# example:
python scripts/import_articles_since_date.py 2023-12-01
```

After the initial import you can set the script to run daily without arguments. This way it will check the database for 
the last date that was imported and import all the articles published after that date. I am on Mac and I have plist 
script/com.user.importarticles.plist for setting up the job via launchctl:
```bash
sudo cp scripts/com.user.importarticles.plist /Library/LaunchDaemons
sudo sudo launchctl bootstrap system /Library/LaunchDaemons/com.user.importarticles.plist
```

## Tests
Run tests in directory root with:
``` bash
pytest
```