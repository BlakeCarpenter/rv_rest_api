#  Documentation for Visits REST API #

## Installation ##
`pip install -r requirements.txt`
`python app.py`
Alternatively, if Docker is installed
`docker-compose up --build -d`

On the database side, database_schema.sql will create the DB and tables for the application. database_setup.sql will provide the database with test data.
The database must be a MySQL database. To connect to the db, the user should create a 'mysql_config.py' similar to 'mysql_config_example.py', with credentials for a MySQL user with access to the database.

## Available API Functions ##

### GET /state/{state}/cities ###
Given a state id, list all cities in the state in alphabetical order.
#### Requires
* `state`: State abbreviation (e.g. 'AL', 'AZ')

#### Status Codes
* Status `200 OK` if successful

`http://localhost:5000/state/AL/cities`
returns as:
```
[
    {
        "city_id": 152,
        "city_name": "Adamsville"
    },
    {
        "city_id": 3,
        "city_name": "Addison"
    },
    ...
]
```

### GET /user/{user}/visits ###
Given a user id, list all cities the user has recorded visiting.
#### Requires
* `user`: Numeric user ID

#### Status Codes
* Status `200 OK` if successful

`http://localhost:5000/user/1/visits`
returns as:
```
[
    {
        "city_id": 1,
        "city_name": "Akron"
    },
    {
        "city_id": 4,
        "city_name": "Montgomery"
    }
]
```
### POST /user/{user}/visits ###
Allow to create rows of data to indicate they have visited a particular city.
#### Requires
* `user`: Numeric user ID

#### Status Codes
* Status `200 OK` if successful
* Status `400 Bad Request` if the request cannot be completed and a error message in the payload as follows:

```
{
    'error': 'Content must be passed as JSON'
}
```

`POST http://localhost:5000/user/1/visits`
with the JSON data

```
{
	"city": "Akron",
	"state": "AL"
}
```

returns as

```
{
    "city_id": 1,
    "id": 15,
    "user_id": "1"
}
```

where `id` is the ID of the visit record

### DEL /user/{user}/visit/{visit} ###
Allow a user to remove an improperly pinned visit.
#### Requires
* `user`: Numeric user ID
* `visit`: Numeric visit ID

#### Status Codes
* Status `200 OK` if successful

### GET /user/{user}/visits/states ###
Return a list of states the user has visited
#### Requires
* `user`: Numeric user ID

#### Status Codes
* Status `200 OK` if successful

`http://localhost:5000/user/1/visits/states`
returns as:
```
[
    {
        "id": 3,
        "state": "Arizona"
    },
    {
        "id": 1,
        "state": "Alabama"
    }
]
```

### GET /city/{city}/suggest/{distance} ###
Returns the most visited city within requested miles. If no visits are found, returns the closest city within requested miles.
#### Requires
* `city`: Numeric city id of city to start from
* `distance`: Radius, in miles

#### Status Codes
* Status `200 OK` if successful

`localhost:5000/city/1/suggest/2000`
returns as:
```
{
    "suggested_city": "Montgomery"
}
```

### GET /teapot ###
Returns Status 418.
#### Requires

#### Status Codes
* Status `418 I'M A TEAPOT`