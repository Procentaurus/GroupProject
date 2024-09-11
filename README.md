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
- create new python virtual environment for ApiComponent inside its folder -> python -m venv venv
- install all needed dependencies for the venv -> pip install -r requirements.txt
- run docker-compose file -> docker-compose up. It creates:
  - Redis container
  - SocketComponent container
  - 2 PostreSQL containers, 1 for each backend component
- create tables in the database for ApiComponent -> python manage.py makemigrations and python manage.py migrate
- run scripts that start ApiComponent from main repo folder -> ./api ./api_thread

<br>Congratulations, you have successfully installed the best online game
  

## Functional modules
- gameApi : module implements and shares a RESTful api responsible for communicating with frontend about all issues except the game itself
- gameMechanics : stores implementation of game mechanics and mechanisms used during the play
- gameNewtorking : contains of implementation of websocket responsible for the connecting players and later the game
