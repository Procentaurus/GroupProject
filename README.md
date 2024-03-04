# Online Multiplayer Game XXXXX
The repository contains source code of game's backend including all tests and additional files
<br>For information about frontend part of game check the repo: [https://github.com/Cyryl-Tokarczyk/group-project-frontend](https://github.com/Cyryl-Tokarczyk/group-project-frontend)

## Technology
  Backend part of the game is implemented in python with usage of its web framework Django,
  especially its 2 modules Django Rest Framework and Djago Channels. For users authentication and authtorization django is used for
  django-simplejwt.


## Installation
- ensure you have python and docker installed on your host system
- clone the repo
- create new python virtual environment -> python -m venv venv
- activate your venv -> venv\Scripts\activate
- install all needed dependencies -> pip install -r requirements
- run docker-copmose file that creates container with websocket layer - redis and db container  - postgresql -> docker-compose up
- create tables in the database -> python manage.py makemigrations and python manage.py migrate
- activate server -> python manage.py runserver

  <br><br>Congratulations, you have successfully installed the best online game
  

## What is inside
- WebGame : main module that contains all configuration
- customUser : module contains implementation of all mechanics connected with user, his creation and actions
- gameApi : module implements and shares a RESTful api responsible for communicating with frontend about all issues except the game itself
- gameMechanics : stores implementation of game mechanics and mechanisms used during the play
- gameNewtorking : contains of implementation of websocket responsible for the connecting players and later the game

