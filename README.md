# Parea
Implementation of easyRASH project with Django (for TechWeb2016)

[Live Demo!](http://ltw1530.web.cs.unibo.it) : deployed on laboratory machines of University of Bologna

A quick tour video cast, recorded on local macOS host: [part 1](https://www.youtube.com/watch?v=nekeqqsmqm8&feature=youtu.be) , [part 2](https://www.youtube.com/watch?v=AbdVEeAkHR8&feature=youtu.be)


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
