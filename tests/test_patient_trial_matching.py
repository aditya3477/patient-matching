#!/usr/bin/env python
# coding: utf-8

# In[1]:


import unittest
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# Import all the functions you are testing
# from your_script import check_age, check_conditions, is_patient_eligible_for_trial, parse_trial_xml, Patient

# Test cases for core functions
class TestPatientTrialMatching(unittest.TestCase):

    def setUp(self):
        # This function runs before each test and sets up the necessary objects
        self.patient = Patient(patient_id='12345', birth_date='1985-05-15', conditions=['diabetes', 'hypertension'])
        self.trial_data = {
            'Trial ID': 'NCT00123456',
            'Title': 'Diabetes Study',
            'Inclusion/Exclusion Criteria': 'Inclusion: Age > 18; Exclusion: Renal failure',
            'Minimum Age': '18 Years',
            'Maximum Age': 'N/A'
        }

    def test_check_age(self):
        # Test if the patient age matches the criteria
        self.assertTrue(check_age(self.patient, '18 Years', 'N/A'))  # Age is 35, should pass
        self.assertFalse(check_age(self.patient, '40 Years', 'N/A'))  # Should fail, min age is 40

    def test_check_conditions(self):
        # Test if the patient's conditions match the exclusion criteria
        exclusion_criteria = "Exclusion: Renal failure, Blindness"
        self.assertTrue(check_conditions(self.patient, exclusion_criteria))  # Should pass
        self.patient.conditions.append('renal failure')
        self.assertFalse(check_conditions(self.patient, exclusion_criteria))  # Should fail

    def test_is_patient_eligible_for_trial(self):
        # Test eligibility for the patient based on the trial data
        eligible, criteria_met = is_patient_eligible_for_trial(self.patient, self.trial_data)
        self.assertTrue(eligible)  # Should pass the criteria
        self.assertIn("age criteria", criteria_met)

    def test_parse_trial_xml(self):
        # Create a mock XML structure for a trial and test parsing
        trial_xml = Element('clinical_study')
        id_info = SubElement(trial_xml, 'id_info')
        nct_id = SubElement(id_info, 'nct_id')
        nct_id.text = 'NCT00123456'

        brief_title = SubElement(trial_xml, 'brief_title')
        brief_title.text = 'Diabetes Study'

        eligibility = SubElement(trial_xml, 'eligibility')
        criteria = SubElement(eligibility, 'criteria')
        textblock = SubElement(criteria, 'textblock')
        textblock.text = 'Inclusion: Age > 18; Exclusion: Renal failure'

        min_age = SubElement(eligibility, 'minimum_age')
        min_age.text = '18 Years'
        max_age = SubElement(eligibility, 'maximum_age')
        max_age.text = 'N/A'

        # Convert the ElementTree to a string for testing
        trial_data_xml = tostring(trial_xml)

        # Save XML to a file for testing (or mock it in other cases)
        with open("test_trial.xml", "wb") as f:
            f.write(trial_data_xml)

        parsed_data = parse_trial_xml("test_trial.xml")
        self.assertEqual(parsed_data['Trial ID'], 'NCT00123456')
        self.assertEqual(parsed_data['Title'], 'Diabetes Study')
        self.assertEqual(parsed_data['Minimum Age'], '18 Years')


# In[2]:


class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Mocking a simple patient and trial data to test the full process
        self.patient_data = [
            Patient(patient_id='12345', birth_date='1985-05-15', conditions=['diabetes', 'hypertension']),
            Patient(patient_id='67890', birth_date='2000-02-25', conditions=['asthma'])
        ]

        self.trial_data_list = [
            {
                'Trial ID': 'NCT00123456',
                'Title': 'Diabetes Study',
                'Inclusion/Exclusion Criteria': 'Inclusion: Age > 18; Exclusion: Renal failure',
                'Minimum Age': '18 Years',
                'Maximum Age': 'N/A'
            },
            {
                'Trial ID': 'NCT00987654',
                'Title': 'Asthma Study',
                'Inclusion/Exclusion Criteria': 'Inclusion: Age > 18',
                'Minimum Age': '18 Years',
                'Maximum Age': '30 Years'
            }
        ]

    def test_full_matching_process(self):
        # Test the full patient-trial matching process
        results = process_patients_and_trials(self.patient_data, self.trial_data_list)

        # Patient 1 should be eligible for the Diabetes study
        self.assertEqual(len(results[0]['eligibleTrials']), 1)
        self.assertEqual(results[0]['eligibleTrials'][0]['trialId'], 'NCT00123456')

        # Patient 2 should be eligible for the Asthma study
        self.assertEqual(len(results[1]['eligibleTrials']), 1)
        self.assertEqual(results[1]['eligibleTrials'][0]['trialId'], 'NCT00987654')


# In[ ]:




