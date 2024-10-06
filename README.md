# Patient-matching
## Prerequisites
Before running this project, ensure that you have the following installed:

1. Python 3.x
2. All the libraries using the requirements.txt
3. Anthropic API key (for generating natural language explanations)

# Setup
## Step 1: Clone the Repository

First clone the repository. The files and folders are structured in a way, to run the main code and the unit tests as well.

## Step 2: Prepare you data
Place the following CSV files in the main directory:

allergies.csv\
careplans.csv\
conditions.csv\
encounters.csv\
immunizations.csv\
medications.csv\
observations.csv\
patients.csv\
procedures.csv

Also, in the folder "NCT0099xxxx" place all trial XML files.

## Step 3: Set Up the API Key
You will need Anthropic’s Claude API to generate natural language explanations. There is a variable in the for storing your API key.

