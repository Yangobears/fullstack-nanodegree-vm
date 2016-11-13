# Item Catalog

This app is an platform that allows user to sign in and post item in different
categories

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

```
Python 2.7
Flask
```

## Database

Used sqlite, so the data is in the file itemcatalogusers.db. You can skip the following
steps unless you would like to start fresh, (delete all records in User, Item and Category)
and add the new category, just run

```
python database_setup.py
```
Then
```
python categories_setup.py
```

## Server

To get the server running, simple do in the vm

```
python main.py
```

To access it in your browser, make sure in your Vagrantfile, have

```
config.vm.network "forwarded_port", guest: 8181, host: 8181
```

Then open your browser and visit
```
localhost:8181
```

## Built With

* [Flask](https://flask.pocoo.org/) - The web framework
* [Google Sign In](https://developers.google.com/identity/sign-in/web/backend-auth) - Authentication
