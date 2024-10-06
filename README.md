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

# Data Sources
For the patient data (with conditions), various csv files are used as input. This is from [synthea](https://synthea.mitre.org/downloads) website, with only the latest 100 data samples. With respect to the clinical trial data, when I tried to access the clinicaltrials.gov API there were issues as it was migrated. So from the [website](https://www.trec-cds.org/2022.html#documents) provided in the google docs, part 1 of the corpus was considered. 
From this it is evident that only a small amount of data was considered. This is due to the fact that I was not able to make use of powerful hardware/systems. Even with google colab pro, the notebook kept crasing due to the large amount of data. 
