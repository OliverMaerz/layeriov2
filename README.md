# layeriov2
layer.io test project based on fastapi by Oliver Maerz

### Setup

Setup an environemnt with Python 3.7 (for example with Anaconda 
```conda create -n layeriov2 python=3.7 && conda activate layeriov2```) and install the dependecies with:

```conda install sqlalchemy mysqlclient``` (or pip install ...)

```pip install fastapi[all]``` (pip because not available in conda)

```pip install python-pcre``` (pip because not available in conda)

Or alternatively:

```pip install -r requirements.txt```

The application requires mariadb (or mysql) as the rdms. 

It is preconfigured for a database called "layerio" running on localhost with user "layeriou" and 
password "tnQtS0jKmUpEp2tb9HSVX8gI9PgBwc". The setting is in the layerio/model.py around line 11

Start the API server locally with 

```uvicorn app.main:app --reload```

### Docker

To run the docker container run:
```shell
docker build -t layeriodemo .
docker run -d --name layeriocontainer -p 80:80 layeriodemo
```
(or alternatively run on other local port like 8080)


### Regex: 
The regular expression (PCRE version) on the PDF allowed whitespace in the sheet names without quotes. 
Also, the column and row identifiers were limited to one character (one number) which might be a little too small 
especially for the resulting row range from only 1-9. Most programs allow rows in the 7 digit range 
(for example '1000000') and columns in the 3 character range (for example 'AAA'). 

Usability wise it probably also makes sense to allow lower case character as input and just convert them to upper case.

So I ended up with a slightly modified version of the regex:

`^((?>(>?'[\w\s]+')|(>?[\w]+))(?>![a-z,A-Z]{1,3}[0-9]{1,7})?(?>:[a-z,A-Z]{1,3}[0-9]{1,7})?)`

There are of course a lot of other factors to consider. For example, accept other valid UTF8 characters that Excel, 
Google Sheet etc. support - especially umlaut for the German market. 
Generally, I would recommend using multiple strings instead of one with the "!" and ":" separators. 
So one string for the name itself, one for the start-column, start-row, end-column, and end-row. 


### Where to put the code for new documents?
I created a MasterSheet class (obviously it does not do too much at this point, but it should give you a rough idea what it could look like). See the file `layerio/mastersheet.py`
Then for every document, an instance of the MasterSheet class could be instantiated.


### API Design

When designing the API, I tried to come up with an easy to use solution with intuitive URI's, online documentation 
and based on common standards (OpenAPI). Considering this plus all the requirements I came up with a solution 
using the FastAPI micro framework. It generates an OpenAPI compliant documentation at
`/docs` (i.e. `http://localhost:8000/docs`) and supports asynchronous API requests. 

### Sample cURL requests

To create a sharing with multiple recipients (users) and multiple shares:

```shell
curl -X PUT \
  http://127.0.0.1:8000/sharings/ \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Host: 127.0.0.1:8000' \
  -H 'Postman-Token: 35a18668-9d5a-44b2-9d06-b0d6ddeb5aba,76a4c60e-cc41-427a-9ba0-5c4216b74201' \
  -H 'User-Agent: PostmanRuntime/7.13.0' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -H 'content-length: 391' \
  -d '{
    "emails": [
        "oliver1@berlinco.com",
        "oliver2@berlinco.com",
        "oliver3@berlinco.com",
        "oliver4@berlinco.com",
        "oliver5@berlinco.com",
        "oliver6@berlinco.com",
        "oliver7@berlinco.com"
    ],
    "sharings": [
        "'\''HRReport'\''!AAA12:CCC59",
        "'\''Actuals'\''!AAA39:CCC45",
        "'\''Assumptions'\''",
        "'\''Dashboard'\''!A1"
    ]
}'
```

To receive all sharings for the current user (so all selections, all recipients etc.):
```shell
curl -X GET \
  http://127.0.0.1:8000/sharings/ \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Host: 127.0.0.1:8000' \
  -H 'Postman-Token: 86cc1a84-615f-41f8-bc65-238515e8b6dd,98fb7c65-c052-4ee0-9e8b-d0695619e21f' \
  -H 'User-Agent: PostmanRuntime/7.13.0' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache'
```

To receive just a list of sharing_id's for the current user:
```shell
curl -X GET \
  http://127.0.0.1:8000/sharings/id \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Host: 127.0.0.1:8000' \
  -H 'Postman-Token: 5987969c-ed7d-42fb-9214-e2cf6e49a085,13b471d1-9e91-41c6-bc59-329a4d4eb732' \
  -H 'User-Agent: PostmanRuntime/7.13.0' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache'
```
The result body of the response for a user with 10 sharings could look like this:
```json
{
    "sharings": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        11,
        13
    ]
}
```


To receive a list of selections for a particular share by share_id 
(in the example below share_id=1):

```shell
curl -X GET \
  http://127.0.0.1:8000/sharings/1/selections \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Postman-Token: 4668f7f9-e825-41b1-9402-3f3f4a280224,657cd984-ba75-49a3-90db-0c10ee8b33a3' \
  -H 'User-Agent: PostmanRuntime/7.13.0' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -H 'referer: http://127.0.0.1:8000/sharings/1/selections'
```
... which would return the something like the following JSON in the body:
```json
{
    "selections": [
        {
            "sheet_name": "HRReport",
            "to_row": 59,
            "from_row": 12,
            "share_id": 11,
            "selection_id": 29,
            "to_column": "CCC",
            "from_column": "AAA"
        },
        {
            "sheet_name": "Actuals",
            "to_row": 45,
            "from_row": 39,
            "share_id": 11,
            "selection_id": 30,
            "to_column": "CCC",
            "from_column": "AAA"
        },
        {
            "sheet_name": "Assumptions",
            "to_row": null,
            "from_row": null,
            "share_id": 11,
            "selection_id": 31,
            "to_column": null,
            "from_column": null
        },
        {
            "sheet_name": "Dashboard",
            "to_row": null,
            "from_row": 1,
            "share_id": 11,
            "selection_id": 32,
            "to_column": null,
            "from_column": "A"
        }
    ]
}
```

Finally to receive just the recipient email addresses (users) as a list for a particular share, use the following request 
(again in the example share_id=1):
```shell
curl -X GET \
  http://127.0.0.1:8000/sharings/1/users \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Postman-Token: e5186f8c-8e3b-4906-adef-dc3926edbf6a,cf885d46-c4b7-48e7-9b29-af77e24f2a34' \
  -H 'User-Agent: PostmanRuntime/7.13.0' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -H 'referer: http://127.0.0.1:8000/sharings/11/users'
``` 
... and this returns a response body like the following:

```json
{
    "users": [
        "oliver1@berlinco.com",
        "oliver2@berlinco.com",
        "oliver3@berlinco.com",
        "oliver4@berlinco.com",
        "oliver5@berlinco.com",
        "oliver6@berlinco.com",
        "oliver7@berlinco.com"
    ]
}
```
