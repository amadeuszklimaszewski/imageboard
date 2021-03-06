# imageboard
* Django-based API for uploading PNG and JPG images.
* Secured with dj-rest-auth and JWT.

## Functionality
* SwaggerUI docs available at `localhost:8000/api/swagger` (DEBUG=True only).  
* Registration process is omitted, users are to be created using django-admin panel. 
* Every user needs an account, which declares which membership user has. There are 3 base memberships declared in fixtures: Basic, Premium and Enterprise. New ones can be added by an admin. 
* Each user can view the list of his images and upload new ones. In return, depending on the membership, he gets link to thumbnails (sizes of which are declared through ManyToMany field), original image and link where a temporary ImageAccessToken can be generated for a limited access to the image. 
* After access token expires, it is deleted on retrieval.

## Tech stack
* Django 4.0
* Django REST Framework
* Docker
* PostgreSQL
* Nginx

## Setup
1. Clone repository:
`$ git clone https://github.com/amadeuszklimaszewski/imageboard/`
2. Run in root directory:
`$ make build`
4. Run project: `make up`


## Fixtures
`$ make fixtures`

## Tests
`$ make test`

## Create admin
`$ make superuser`

## Makefile
`Makefile` contains useful command aliases
