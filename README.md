# Reddit API Client Registration

1. Register a Reddit account.
2. Go to [Reddit Apps](https://www.reddit.com/prefs/apps).
3. Choose 'Script' and fill in all other fields with the appropriate data. Set "redirect uri" to `https://www.reddit.com/`.

# Main Script

Clone the git repository or extract it from a .zip file.

## For Cloning the Repository

1. Open terminal and do steps below
2. Clone the repository:
    ```sh
    git clone https://github.com/Nertwy/PLACEHOLDER.git
    ```
3. Navigate to the project directory:
    ```sh
    cd Maksym_Afanasiev_Reddit_task
    ```

## For Extracted .zip

1. Extract the files to the desired folder.
2. Move to the extracted `Maksym_Afanasiev_Reddit_task` folder and open the folder in the terminal.

## Manage Virtual Environment (For both Extract and git clone!)

1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
2. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On Linux:
        ```sh
        source ./venv/bin/activate
        ```
3. Install the required packages:
    ```sh
    pip install -r .\requirements.txt
    ```

## Create .env File

1. Create a [.env](http://_vscodecontentref_/4) file in the root directory of the project.
2. Add your Reddit sensitive data to the [.env](http://_vscodecontentref_/5) file:
    ```
    CLIENT_ID=your_client_id
    CLIENT_SECRET=your_client_secret
    USER_AGENT=RedditScript/0.1 by YourRedditUsername
    ```

## Run Program
1. Run the script with the following command:
    ```sh
    python .\main.py "input file path.xlsx" "output file path.xlsx"
    ```
    **Important Note:** It is recommended to use absolute paths for the input and output files, as relative paths are based on the Python virtual environment's location and could be confusing.

## Alternative Run
1. Run the [start.ps1](http://_vscodecontentref_/6) script on Windows:
    ```ps1
    .\start.ps1
    ```
2. Run the [start.sh](http://_vscodecontentref_/7) script on Linux:
    ```sh
    ./start.sh
    ```

3. Follow the prompts to enter the input URL path and output file path.