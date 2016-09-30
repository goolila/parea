# Parea
Implementation of easyRASH project with Django (for TechWeb2016)

##Installation

Note: using a virtual environment is recommended. After activing your virtualenv, enter following commands to start the project.

Clone this repository
`git clone https://github.com/sheshkovsky/parea`

Go to project directory
`cd parea/`

Install requirements
`pip install -r requirements.txt`

##Usage
Create database tables
`./manage.py makemigrations conference`

`./manage.py migrate`

Create a superuser
`./manage.py createsuperuser`

Run server
`./manage.py runserver`

* utils.py is excluded temporarily!
