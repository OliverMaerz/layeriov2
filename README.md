# layeriov2
layer.io test project based on fastapi

### Setup

Setup an environemnt with Python 3.7 (for example with Anaconda ```conda create -n layeriov2 python=3.7 && conda activate layeriov2```) and install the dependecies with:

```conda install sqlalchemy mysqlclient``` (or pip install ...)

```pip install fastapi[all]``` (not available in conda)

```pip install python-pcre``` (not available in conda)

Or alternatively:

```pip install -r requirements.txt```

Start the server with 

```uvicorn main:app --reload```
