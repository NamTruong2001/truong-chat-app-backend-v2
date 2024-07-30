# truong-chat-app-backend-v2
PET project

## Descriptions:
A backend for chat application, used to handle real-time chat message of users
- Features:
  - Private/Group conversations
  - Online status of other connected users
  - Read status of private conversation
  - Log in
  - Sign up
 
This is truong-chat-app-backend but shifting application code to use with mongodb
  - Technologies:
    - Fast API
    - Python socket.io
    - MongoDB
    - Redis
   

## Prerequisites
- Python >= 3.9
- MongoDB
- Redis

- In the project directory, run the command below to install the dependencies
```
pip install -r requirements.txt
```
- Cd to app directory
- Finish the config file, config file name can be .local (for local development), .dev,...
- Run the command below to start the project (-p: port, -e: config file name with no dot, assocaiate with enviroment)
```
python main.py -p 8000 -e local
```
  
