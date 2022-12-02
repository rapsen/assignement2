## Introduction

  This is the repo for the assignement 2 of Industrial Informatics 2022
  
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
