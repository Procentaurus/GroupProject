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
- run docker-compose file that creates:
  - Redis container
  - SocketComponent container
  - ApiComponent container
  - Nginx container
  - 2 PostreSQL containers, 1 for each component
  ```
  docker-compose up
  ```

<br>Congratulations, you have successfully installed the best online game


## Functional modules
- gameApi : module implements and shares a RESTful api responsible for communicating with frontend about all issues except the game itself
- gameMechanics : stores implementation of game mechanics and mechanisms used during the play
- gameNewtorking : contains of implementation of websocket responsible for the connecting players and later the game
