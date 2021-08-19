# Auth0 + Python + FastAPI API Seed

This is the seed project you need to use if you're going to create an API using FastAPI in Python and Auth0. If you just want to create a Regular Python WebApp, please check [this project](https://github.com/auth0-samples/auth0-python-web-app/tree/master/01-Login)

## Running the example

In order to run the example you need to have `python3` (any version higher than `3.6`) and `pip3` installed.

### Configuration

### Configuration

The configuration you'll need is mostly information from Auth0, you'll need both the tentant domain and the API information.

This app reads its configuration information from a `.config` file by default.

To create a `.config` file you can copy the `.example.config` file and fill the values accordingly:

```console
cp .example.config .config
# update the config file for the correct values
export ENV='.config'
```

You can change this behavior by setting the following environment variables (remember to update the values accordingly):

```console
export ENV='variables'
export DOMAIN='your.domain.auth0.com'
export API_AUDIENCE='your.api.audience'
export ISSUER='https://your.domain.auth0.com'
export ALGORITHMS='RS256'
```

### Spin up the server

Once you've set your environment information below you'll find the commands you'll need.

1. Create and activate a python environment:

```console
python3 -m venv .env
source .env/bin/bash
```

2. Install the needed dependencies with:

```console
pip install -r requirements.txt
```
3. Start the server with the following:

```console
uvicorn application.main:app
```

4. Try calling [http://localhost:8000/api/public](http://localhost:8000/api/public)

```
curl -X 'GET' \
  'http://localhost:8000/api/public' \
  -H 'accept: application/json'
```

## API documentation

Access [http://localhost:8000/docs](http://localhost:8000/docs). From there you'll see all endpoints and can test your API

### Testing the API

#### Private endpoint

You can then try to do a GET to [http://localhost:8000/api/private](http://localhost:8000/api/private) which will throw an error if you don't send an access token signed with RS256 with the appropriate issuer and audience in the Authorization header.

```console
curl -X 'GET' \
  'http://localhost:8000/api/private' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer  <FILL YOUR TOKEN HERE>'
```

#### Private-Scoped endpoint 

You can also try to do a GET to [http://localhost:8000/api/private-scoped](http://localhost:8000/api/private-scoped) which will throw an error if you don't send an access token with the scope `read:messages` signed with RS256 with the appropriate issuer and audience in the Authorization header.

```console
curl -X 'GET' \
  'http://localhost:8000/api/private-scoped' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer  <FILL YOUR TOKEN WITH SCOPES HERE>'
```
