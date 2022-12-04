## Introduction

  This is the repository for the assignement 2 of Industrial Informatics 2022
  
  Here is the subject: https://moodle.tuni.fi/pluginfile.php/2861557/mod_resource/content/0/E7%20Assignment%202.pdf
  
  Here is our solution deployed: https://assignement2.azurewebsites.net/

## Installation

_Below is the instruction to create the environment and run locally the web application._

1. Clone the repository

   ```sh
   git clone https://github.com/rapsen/assignement2.git
   ```
   
2. Create and activate the python virtual environement (python <= 3.9)

    Windows:
    
    ```sh
    py -m venv .venv
    .venv\scripts\activate
    ```

    macOS/Linux:
    
    ```sh
    python3 -m venv .venv
   source .venv/bin/activate
    ```
    
4. Install the requirements

    ```sh
    pip install -r requirements.txt
    ```
    
5. Run the following command
   ```sh
   ./start.sh
   ```
   
6. Browse to the application at http://localhost:5000 in a web browser.

## Roadmap
- [x] Mock data with MQTT client
- [x] Subscribe and receive MQTT data
- [x] Create a DB table and insert sample data
- [x] Fetch data from the DB table
- [x]  Insert the received MQTT data into the DB table
- [x] Create an HTTP endpoint and retrieve some mocked data
- [x] Retrieve the DB data from the HTTP endpoint
- [x] Integration
- [x] Business logic
- [x] Deploy the solution with Azure

## Requirements
  - [x] Back end is able to handle a fixed amount of 10 robots
  - [x] Create a web UI tha provides the next features:
    - [x] Real-time data
    - [x] Historical data
    - [x] Alarms
  - [x] Real time Dashbaord
     - [x] Latest state of given robot
  - [x] Hictorical Data
    - [x] User filters by robotId and time window
    - [x] Show two KPIs for this filtered data
      - [x] Percentage of time in each state
      - [x] MTBF: Mean Time between Failures
  - [ ] Alarms
    - [ ] Log if a robot has been more than X amount of time in IDLE state
    - [ ] Log if a robot has been more than Y amount of time in DOWN state
    

    
