# Auto-Scaling Function Manager

## Overview
This project implements a simple function manager that automatically scales based on incoming messages. Each message triggers a function that processes the message, sleeps for 5 seconds, and writes the message to a shared file.

## How to Run
NOTE: the commands below written to run from auto_scale

### Local Setup
1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. Run the application:
    ```
    uvicorn main:app --reload
    ```

3. Test the API:
    ```
    curl --header "Content-Type: application/json" --request POST --data '{"message":"Test message"}' http://localhost:8000/messages
    ```

4. Get statistics:
    ```
    curl http://localhost:8000/statistics
    ```


## Running Tests
Run tests using pytest:
    '''
    pytest
    '''