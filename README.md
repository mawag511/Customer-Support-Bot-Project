# CustomerSupportBot

## Final diploma project: Creation of customer support bot in python for telegram channels of stores that sell technical and electronic equipment
### Includes:
- JSON file with exemplary training data;
- Jupyter Notebook file containing the training of the bot's AI model;
- Python files with bot and notifier;
- SQLite DB
- Tests

### Bot includes:
- Greets;
- Answers company information requests;
- Finds injector in DB based on user's message and prints its information;
- Checks for availability of injector in DB based on user's message;
- Remembers user's request in case the needed injector is not available, then sends notification when injector's available (based on user's preference)

## Installation preparation:
- After downloading the zip file, create a virtual environment and install the requirements within it with the command: 
  python -m pip install -r requirements.txt
- Add your bot Token and, if integration test is needed, add API ID and API Hash
- If the folder name is changed, update the path in predictions_test.py if needed
