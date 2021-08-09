# Auth0 + Python + FastAPI API Seed

This is the seed project you need to use if you're going to create an API using FastAPI in Python and Auth0. If you just want to create a Regular Python WebApp, please check [this project](https://github.com/auth0-samples/auth0-python-web-app/tree/master/01-Login)

<!--
Please check our [Quickstart](https://auth0.com/docs/quickstart/backend/python) to better understand this sample.
-->

## Running the example

In order to run the example you need to have `python3` (any version higher than `3.6`) and `pip3` installed.

### Configuration

This app is prepared to be deployed to a production environment which means you can create environment variables for running it both on production or development envs let's see how that looks.

There are two ways you can configure and fill the necessary variables:

1. Creating environment variables; or
1. Creating a `.config` file to hold said variables values

For the **first** approach you'll need 4 variables (remember to update the values accordingly):

```console
export DOMAIN='your.domain.auth0.com'
export API_AUDIENCE='your.api.audience'
export ALGORITHMS='RS256'
export ENV='variables'
```

For the **second** approach you can copy the `.example.config` file and fill the values accordingly:

```console
cp .example.config .config
# update the config file for the correct values
export ENV='.config'
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

<!--
## Running the example with Docker

In order to run the sample with [Docker](https://www.docker.com/) you need to add the `AUTH0_DOMAIN` and `API_ID`
to the `.env` filed as explained [previously](#running-the-example) and then

1. Execute in command line `sh exec.sh` to run the Docker in Linux, or `.\exec.ps1` to run the Docker in Windows.
2. Try calling [http://localhost:8000/api/public](http://localhost:8000/api/public)
-->
