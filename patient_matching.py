#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

allergies_path = 'allergies.csv'
careplans_path = 'careplans.csv'

# Read the files into dataframes
allergies_df = pd.read_csv(allergies_path)
careplans_df = pd.read_csv(careplans_path)

allergies_df.dropna()
careplans_df.dropna()
# Check for common PATIENT and ENCOUNTER values between the two datasets
common_patients = pd.Series(list(set(allergies_df['PATIENT']).intersection(set(careplans_df['PATIENT']))))
common_encounters = pd.Series(list(set(allergies_df['ENCOUNTER']).intersection(set(careplans_df['ENCOUNTER']))))

# Display the counts of common patients and encounters
common_patients_count = len(common_patients)
common_encounters_count = len(common_encounters)

common_patients_count, common_encounters_count

common_columns = set(careplans_df.columns).intersection(set(allergies_df.columns))
print("Common columns:", common_columns)


# In[2]:


allergies_df_dedup = allergies_df.drop_duplicates(subset=['PATIENT'])
careplans_df_dedup = careplans_df.drop_duplicates(subset=['PATIENT'])

# Perform the merge after deduplication
merged_df = pd.merge(careplans_df_dedup, allergies_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_allergies'))

# remove the duplicate columns
merged_df.drop([i for i in merged_df.columns if 'allergies' in i],
               axis=1, inplace=True)

merged_df.shape


# In[3]:


merged_df.shape


# In[4]:


# Load the newly provided file (conditions.csv)
conditions_path = 'conditions.csv'

# Read the file into a dataframe
conditions_df = pd.read_csv(conditions_path)

conditions_df_dedup = conditions_df.drop_duplicates(subset=['PATIENT'])

# Merge the conditions dataset with the already merged allergies and careplans dataset
# Perform the merge after deduplication
merged_all_data = pd.merge(merged_df, conditions_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_conditions'))


merged_all_data.drop([i for i in merged_all_data.columns if 'conditions' in i],
               axis=1, inplace=True)

merged_all_data.shape


# In[5]:


# Load the newly provided file (encounters.csv)
encounters_path = 'encounters.csv'

# Read the file into a dataframe
encounters_df = pd.read_csv(encounters_path)

encounters_df_dedup = encounters_df.drop_duplicates(subset=['PATIENT'])

merged_encounter = pd.merge(merged_all_data, encounters_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_encounters'))

merged_encounter.drop([i for i in merged_encounter.columns if 'encounters' in i],
               axis=1, inplace=True)

# Load the newly provided file (encounters.csv)
immunizations_path = 'immunizations.csv'

# Read the file into a dataframe
immunizations_df = pd.read_csv(immunizations_path)

immunizations_df_dedup = immunizations_df.drop_duplicates(subset=['PATIENT'])

merged_immunization = pd.merge(merged_encounter, immunizations_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_immunizations'))

merged_immunization.drop([i for i in merged_immunization.columns if 'immunization' in i],
               axis=1, inplace=True)


# In[6]:


# Load the newly provided file (encounters.csv)
medications_path = 'medications.csv'

# Read the file into a dataframe
medications_df = pd.read_csv(medications_path)

medications_df_dedup = medications_df.drop_duplicates(subset=['PATIENT'])

merged_medication = pd.merge(merged_immunization, medications_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_medications'))

merged_medication.drop([i for i in merged_medication.columns if 'medications' in i],
               axis=1, inplace=True)


# In[7]:


# Load the newly provided file (encounters.csv)
observations_path = 'observations.csv'

# Read the file into a dataframe
observations_df = pd.read_csv(observations_path)

observations_df_dedup = observations_df.drop_duplicates(subset=['PATIENT'])

merged_observations = pd.merge(merged_medication, observations_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_observations'))

merged_observations.drop([i for i in merged_observations.columns if 'observations' in i],
               axis=1, inplace=True)

# Load the newly provided file (encounters.csv)
patients_path = 'patients.csv'

# Read the file into a dataframe
patients_df = pd.read_csv(patients_path)

patients_df_dedup = patients_df.drop_duplicates(subset=['PATIENT'])

merged_patients = pd.merge(merged_observations, patients_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_patients'))

merged_patients.drop([i for i in merged_patients.columns if 'patients' in i],
               axis=1, inplace=True)


# Load the newly provided file (encounters.csv)
procedures_path = 'procedures.csv'

# Read the file into a dataframe
procedures_df = pd.read_csv(procedures_path)

procedures_df_dedup = procedures_df.drop_duplicates(subset=['PATIENT'])

# Merge the conditions dataset with the already merged allergies and careplans dataset
final_merged_data =  pd.merge(merged_patients, procedures_df_dedup, on=['PATIENT'], how='inner', suffixes=('', '_procedures'))

final_merged_data.drop([i for i in final_merged_data.columns if 'procedures' in i],
               axis=1, inplace=True)


# In[8]:


final_merged_data.shape


# In[9]:


final_merged_data.drop(columns = ['DEATHDATE', 'STOP', 'REASONCODE', 'REASONDESCRIPTION', 'REACTION1', 'DESCRIPTION1', 'SEVERITY1', 'REACTION2', 'DESCRIPTION2', 'SEVERITY2', 'DRIVERS', 'PASSPORT', 'PREFIX', 'SUFFIX', 'MAIDEN', 'MARITAL', 'ZIP'])


# In[10]:


import os
import xml.etree.ElementTree as ET
from datetime import datetime
import openai
import json


# In[11]:


import anthropic
from anthropic import Anthropic


class Patient:
        """
    Represents a patient with their associated information like ID, age, and conditions.

    Attributes:
        patient_id (str): The unique ID of the patient.
        age (int): The patient's age, calculated from the birth date.
        conditions (list): A list of the patient's medical conditions.
    """
    def __init__(self, patient_id, birth_date, conditions):
        
              """
        Initializes the Patient object with ID, birth date, and conditions.

        Parameters:
            patient_id (str): The unique ID of the patient.
            birth_date (str): The patient's birth date in the format '%Y-%m-%d'.
            conditions (list): A list of the patient's medical conditions.
        """
        self.patient_id = patient_id
        self.age = self.calculate_age(birth_date)
        self.conditions = conditions  # List of patient conditions (to be extracted from the dataset)

    @staticmethod
    def calculate_age(birth_date):
        
             """
        Calculate the patient's age based on the birth date.

        Parameters:
            birth_date (str): The patient's birth date in the format '%Y-%m-%d'.

        Returns:
            int: The calculated age of the patient.
        """
        if pd.isna(birth_date):
            return None
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Extracting patient data from CSV
def extract_patient_data(df):
    
        """
    Extracts patient data from a pandas DataFrame and creates a list of Patient objects.

    Parameters:
        df (pandas.DataFrame): The input DataFrame containing patient data.

    Returns:
        list: A list of Patient objects.
    """
        
    patients = []
    for _, row in df.iterrows():
        birth_date = row['START']  # Here START represents birthdate in the given dataset structure
        conditions = [row['DESCRIPTION']]  # Add more logic if there are multiple conditions per patient
        patients.append(Patient(row['PATIENT'], birth_date, conditions))
    return patients

# Function to check age eligibility
def check_age(patient, min_age, max_age):
    
       """
    Checks if a patient's age falls within the trial's minimum and maximum age range.

    Parameters:
        patient (Patient): The patient object containing age.
        min_age (str): The minimum age requirement for the trial (in string format like '18 Years').
        max_age (str): The maximum age requirement for the trial (in string format like '65 Years').

    Returns:
        bool: True if the patient's age is within the specified range, False otherwise.
    """
        
        
    # Convert age strings like '18 Years' to integer
    def age_to_int(age_str):
        if age_str == 'N/A':
            return None
        return int(age_str.split()[0])

    patient_age = patient.age
    min_age = age_to_int(min_age)
    max_age = age_to_int(max_age)

    # Check if the patient's age is within the trial's age range
    if min_age is not None and patient_age < min_age:
        return False
    if max_age is not None and patient_age > max_age:
        return False
    return True

# Function to check condition eligibility
def check_conditions(patient, exclusion_criteria):
    
    """
    Checks if a patient's conditions meet the exclusion criteria of the trial.

    Parameters:
        patient (Patient): The patient object containing conditions.
        exclusion_criteria (list): A list of conditions that exclude a patient from the trial.

    Returns:
        bool: True if the patient's conditions are eligible, False if any condition violates the criteria.
    """
    
    
    excluded_conditions = ["renal failure", "blindness"]  # Example conditions from trial exclusion criteria

    for condition in patient.conditions:
        if condition.lower() in excluded_conditions:
            return False
    return True



def generate_claude_explanation(patient, eligibility_results):
    
        """
    Generates a natural language explanation using Claude API for the patient's eligibility results.

    Parameters:
        patient (Patient): The patient object with age and conditions.
        eligibility_results (dict): The results of eligibility checks (age and conditions).

    Returns:
        str: A natural language explanation of the patient's eligibility.
    """
        
        
    client = Anthropic(api_key="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")
    
    user_message = f"""
    For the following patient, please explain in detail why they are eligible or not for the clinical trial.
    
    Patient Information:
    Age: {patient.age}
    Conditions: {', '.join(patient.conditions)}
    
    Eligibility Results:
    {eligibility_results}
    
    Provide a natural language explanation.
    """
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=50,
        system="You are an AI assistant helping to match patients with clinical trials.",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    
    explanation = response.content
    return explanation
    


# Function to check patient's eligibility for a trial
def is_patient_eligible_for_trial(patient, trial_data):
    
        """
    Determines if a patient is eligible for a given clinical trial based on age and condition criteria.
    
    Parameters:
        patient (Patient): The patient object containing age and conditions.
        trial_data (dict): A dictionary containing the clinical trial information including minimum and maximum age, 
                           and inclusion/exclusion criteria.
    
    Returns:
        tuple: 
            - overall_eligible (bool): True if the patient meets both age and condition eligibility criteria, False otherwise.
            - all_criteria (list): A list of strings that explain which criteria were met or not met, including 
                                   an explanation generated by the Claude API.
    """
        

    eligibility_results = {}
    criteria_met = []
    
    # Check age
    age_eligible = check_age(patient, trial_data['Minimum Age'], trial_data['Maximum Age'])
    if age_eligible:
        criteria_met.append(f"Age requirement met: Patient age {patient.age} within trial range")
    else:
        criteria_met.append(f"Age requirement not met: Patient age {patient.age} outside trial range")
    
    # Check conditions
    conditions_eligible = check_conditions(patient, trial_data['Inclusion/Exclusion Criteria'])
    if conditions_eligible:
        criteria_met.append("All condition requirements met")
    else:
        criteria_met.append("One or more condition requirements not met")
    
    # Generate explanation using Claude
    explanation = generate_claude_explanation(patient, eligibility_results)
    
    # If explanation is a TextBlock, convert it to string
    if hasattr(explanation, 'text'):
        explanation = explanation.text
    
    # Combine criteria_met with explanation
    all_criteria = criteria_met + [explanation]
    
    overall_eligible = age_eligible and conditions_eligible
    return overall_eligible, all_criteria



def parse_trial_xml(xml_file_path):
    
        """
    Parses an XML file to extract clinical trial data for actively recruiting trials.

    Parameters:
        xml_file_path (str): The file path of the clinical trial XML file.

    Returns:
        dict: A dictionary with trial details (ID, title, criteria, age range) if recruiting, None otherwise.
    """
        
        
    try:
        # Load and parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Extract the recruitment status
        recruitment_status = root.find('overall_status').text

        # Only include trials that are actively recruiting
        if recruitment_status.lower() != 'recruiting':
            return None

        # Extract the trial ID, title, inclusion/exclusion criteria, and age range
        trial_id = root.find('id_info').find('nct_id').text
        title = root.find('brief_title').text

        # Extract eligibility criteria
        eligibility = root.find('eligibility')
        criteria_text = eligibility.find('criteria').find('textblock').text.strip()
        min_age = eligibility.find('minimum_age').text if eligibility.find('minimum_age') is not None else 'N/A'
        max_age = eligibility.find('maximum_age').text if eligibility.find('maximum_age') is not None else 'N/A'

        # Return the extracted data
        return {
            'Trial ID': trial_id,
            'Title': title,
            'Inclusion/Exclusion Criteria': criteria_text,
            'Minimum Age': min_age,
            'Maximum Age': max_age,
            'Recruitment Status': recruitment_status
        }
    except Exception as e:
        print(f"Error parsing XML file {xml_file_path}: {e}")
        return None

# Function to parse all XML files in a directory and only include actively recruiting trials
def parse_all_trials(xml_directory):
        """
    Parses all XML files in a directory to extract actively recruiting clinical trials.

    Parameters:
        xml_directory (str): The directory containing clinical trial XML files.

    Returns:
        list: A list of dictionaries with trial data for actively recruiting trials.
    """
        
    trial_data_list = []
    
    # Loop through all files in the directory
    for filename in os.listdir(xml_directory):
        if filename.endswith(".xml"):
            xml_file_path = os.path.join(xml_directory, filename)
            trial_data = parse_trial_xml(xml_file_path)
            if trial_data:  # Only add trials that are actively recruiting
                trial_data_list.append(trial_data)
    
    return trial_data_list

# Main function to process patients and trials
def process_patients_and_trials(patient_data, trial_data_list):
        """
    Processes the patient data and matches them to eligible clinical trials.

    Parameters:
        patient_data (list): A list of Patient objects.
        trial_data_list (list): A list of dictionaries containing trial data.

    Returns:
        list: A list of dictionaries where each patient is mapped to eligible trials.
    """
        
    results = []

    # Iterate through all patients and check eligibility for all trials
    for patient in patient_data:
        patient_results = {"patientId": patient.patient_id, "eligibleTrials": []}

        for trial_data in trial_data_list:
            eligible, criteria_met = is_patient_eligible_for_trial(patient, trial_data)

            if eligible:
                trial_result = {
                    "trialId": trial_data['Trial ID'],
                    "trialName": trial_data['Title'],
                    "eligibilityCriteriaMet": criteria_met
                }
                patient_results["eligibleTrials"].append(trial_result)

        results.append(patient_results)

    return results

    # Load patient data from CSV
patient_data = extract_patient_data(final_merged_data)

xml_directory = 'NCT0099xxxx'  # Specify the directory containing the XML files
trial_data_list = parse_all_trials(xml_directory)
    
    # Process and match patients to trials
results = process_patients_and_trials(patient_data, trial_data_list)




# In[12]:


def write_results_to_excel(patients_with_trials, excel_file='eligible_trials.xlsx'):
    
        """
    Writes the patient and trial matching results to an Excel file.

    Parameters:
        patients_with_trials (list): A list of dictionaries containing patient trial matching information.
        excel_file (str): The file path where the Excel file will be saved.

    Returns:
        None
    """
        
    rows = []
    
    def flatten_and_stringify(item):
        """Helper function to flatten nested lists and convert all items to strings"""
        if isinstance(item, list):
            return ", ".join(flatten_and_stringify(x) for x in item)
        elif hasattr(item, 'text'):  # For TextBlock objects
            return item.text
        else:
            return str(item)
    
    for patient in patients_with_trials:
        patient_id = patient['patientId']
        for trial in patient['eligibleTrials']:
            criteria_met = trial['eligibilityCriteriaMet']
            
            # Use the helper function to handle nested lists and convert to string
            joined_criteria = flatten_and_stringify(criteria_met)
            
            row = {
                'Patient ID': patient_id,
                'Trial ID': trial['trialId'],
                'Trial Name': trial['trialName'],
                'Eligibility Criteria Met': joined_criteria
            }
            rows.append(row)
    
    # Convert the rows into a pandas DataFrame
    df = pd.DataFrame(rows)
    
    # Write the DataFrame to an Excel file
    df.to_excel(excel_file, index=False)
    

write_results_to_excel(results)


# In[14]:


def write_output_json(results, output_file='results.json'):
    
      """
    Writes the patient and trial matching results to a JSON file.

    Parameters:
        results (list): A list of dictionaries containing patient trial matching information.
        output_file (str): The file path where the JSON file will be saved.

    Returns:
        None
    """
        
        
    def serialize_textblock(obj):
        """Custom JSON serializer to handle TextBlock objects"""
        if hasattr(obj, 'text'):  # Check if it's a TextBlock
            return obj.text
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
    
    # Create a deep copy of results to avoid modifying the original data
    serializable_results = []
    
    for patient in results:
        serializable_patient = patient.copy()
        serializable_trials = []
        
        for trial in patient['eligibleTrials']:
            serializable_trial = trial.copy()
            
            # Convert TextBlock to string in eligibilityCriteriaMet
            criteria_met = trial['eligibilityCriteriaMet']
            if isinstance(criteria_met, list):
                serializable_criteria = []
                for criterion in criteria_met:
                    if hasattr(criterion, 'text'):
                        serializable_criteria.append(criterion.text)
                    else:
                        serializable_criteria.append(str(criterion))
                serializable_trial['eligibilityCriteriaMet'] = serializable_criteria
            elif hasattr(criteria_met, 'text'):
                serializable_trial['eligibilityCriteriaMet'] = criteria_met.text
            else:
                serializable_trial['eligibilityCriteriaMet'] = str(criteria_met)
            
            serializable_trials.append(serializable_trial)
        
        serializable_patient['eligibleTrials'] = serializable_trials
        serializable_results.append(serializable_patient)
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, default=serialize_textblock)


# Output results as JSON
write_output_json(results)


# In[ ]:




