# Online Multiplayer Game XXXXX
The repository contains source code of game' backend including all tests and additional files
<br>For information about frontend part of game check the repo : [https://github.com/Cyryl-Tokarczyk/group-project-frontend](https://github.com/Cyryl-Tokarczyk/group-project-frontend)

## Technology
  Backend part of the game is implemented in python with usage of its web framework Django,
  especially its 2 modules Django Rest Framework and Djago Channels used for implementation of the game itself
  and django-simplejwt for users authentication and authtorization.
  
## Installation
- ensure you have python and docker installed on your host system
- clone the repo
- create new python virtual environment : python -m venv venv
- activate your venv : venv\Scripts\activate
- install all needed dependencies : pip install -r requirements
- create database : python manage.py makemigrations and python manage.py migrate
- activate server : python manage.py runserver
- create message layer for websocket : docker run -p 6379:6379 --rm redis:7
  <br><br>Congratulations, you have successfully installed the best online game
  
## What is inside
- WebGame : main module that contains all configuration
- customUser : module contaion implementation of all mechanics connected with user, his creation and actions
- gameApi : module implements and shares a REST api responsible for communicating with frontend about all issues except the game itself
- gameMechanics : stores implementation of game mechanics and mechanisms used during the play
- gameNewtorking : contains of implementation of websocket responsible for the connecting players and later the game

