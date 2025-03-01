from flask import Flask, request, render_template, jsonify
import pandas as pd
from datetime import datetime
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key='YOUR_GEMINI_API_KEY')
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return render_template('personal_details.html')  # Changed to render personal_details.html directly

@app.route('/personal_details')
def personal_details():
    return render_template('personal_details.html')

@app.route('/test_save', methods=['GET'])
def test_save():
    try:
        # Create test data
        test_personal_info = {
            'Full Name': ['Test User'],
            'Age': [30],
            'Gender': ['Male'],
            'Email': ['test@test.com'],
            'Phone': ['1234567890'],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        test_reports = {
            'Patient Name': ['Test User'],
            'Fasting Blood Glucose': [100],
            'Post Prandial Glucose': [140],
            'HbA1c': [5.7],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        # Create DataFrames
        personal_info_df = pd.DataFrame(test_personal_info)
        test_reports_df = pd.DataFrame(test_reports)
        
        # Save to Excel
        with pd.ExcelWriter('data.xlsx') as writer:
            personal_info_df.to_excel(writer, sheet_name='Personal Info', index=False)
            test_reports_df.to_excel(writer, sheet_name='Test Reports', index=False)
        
        return "Test data saved successfully!"
    
    except Exception as e:
        print(f"Test save error: {e}")
        return f"Error saving test data: {e}"

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        data = request.json
        print("Received data:", data)  # Debug print

        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        file_path = os.path.join('reports', 'dataentry.xlsx')
        
        # Prepare data for each sheet
        personal_info = {
            'Full Name': [data['personalInfo']['fullName']],
            'Age': [data['personalInfo']['age']],
            'Gender': [data['personalInfo']['gender']],
            'Email': [data['personalInfo']['email']],
            'Phone': [data['personalInfo']['phone']],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        medical_history = {
            'Patient Name': [data['personalInfo']['fullName']],
            'Diabetes Type': [data['medicalHistory']['diabetesType']],
            'Diagnosis Date': [data['medicalHistory']['diagnosisDate']],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        health_metrics = {
            'Patient Name': [data['personalInfo']['fullName']],
            'Weight (kg)': [data['healthMetrics']['weight']],
            'Height (cm)': [data['healthMetrics']['height']],
            'BMI': [float(data['healthMetrics']['weight']) / ((float(data['healthMetrics']['height'])/100) ** 2)],
            'Blood Pressure': [f"{data['healthMetrics']['systolic']}/{data['healthMetrics']['diastolic']}"],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        test_reports = {
            'Patient Name': [data['personalInfo']['fullName']],
            'Fasting Blood Glucose': [float(data['testReports']['fastingBloodGlucose'])],
            'Post Prandial Glucose': [float(data['testReports']['postPrandialGlucose'])],
            'HbA1c': [float(data['testReports']['hba1c'])],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        lifestyle_info = {
            'Patient Name': [data['personalInfo']['fullName']],
            'Activity Level': [data.get('lifestyle', {}).get('activityLevel', 'Not specified')],
            'Sleep Hours': [data.get('lifestyle', {}).get('sleepHours', 'Not specified')],
            'Diet Preferences': [', '.join(data.get('lifestyle', {}).get('dietPreferences', []))],
            'Date Added': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }

        try:
            # Try to read existing Excel file
            try:
                with pd.ExcelFile(file_path) as xls:
                    df_personal = pd.read_excel(xls, 'Personal Info')
                    df_medical = pd.read_excel(xls, 'Medical History')
                    df_health = pd.read_excel(xls, 'Health Metrics')
                    df_tests = pd.read_excel(xls, 'Test Reports')
                    df_lifestyle = pd.read_excel(xls, 'Lifestyle Info')
            except FileNotFoundError:
                # If file doesn't exist, create empty DataFrames
                df_personal = pd.DataFrame()
                df_medical = pd.DataFrame()
                df_health = pd.DataFrame()
                df_tests = pd.DataFrame()
                df_lifestyle = pd.DataFrame()

            # Create new dataframes with current data
            new_personal = pd.DataFrame(personal_info)
            new_medical = pd.DataFrame(medical_history)
            new_health = pd.DataFrame(health_metrics)
            new_tests = pd.DataFrame(test_reports)
            new_lifestyle = pd.DataFrame(lifestyle_info)

            # Concatenate existing and new data
            df_personal = pd.concat([df_personal, new_personal], ignore_index=True)
            df_medical = pd.concat([df_medical, new_medical], ignore_index=True)
            df_health = pd.concat([df_health, new_health], ignore_index=True)
            df_tests = pd.concat([df_tests, new_tests], ignore_index=True)
            df_lifestyle = pd.concat([df_lifestyle, new_lifestyle], ignore_index=True)

            # Save all sheets to Excel
            with pd.ExcelWriter(file_path) as writer:
                df_personal.to_excel(writer, sheet_name='Personal Info', index=False)
                df_medical.to_excel(writer, sheet_name='Medical History', index=False)
                df_health.to_excel(writer, sheet_name='Health Metrics', index=False)
                df_tests.to_excel(writer, sheet_name='Test Reports', index=False)
                df_lifestyle.to_excel(writer, sheet_name='Lifestyle Info', index=False)

            print("Data saved successfully to all sheets")
            return jsonify({
                'success': True,
                'message': 'Data saved successfully to all sheets'
            })

        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return jsonify({
                'success': False,
                'message': f'Error saving to Excel: {e}'
            }), 500

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            'success': False,
            'message': f'Error processing request: {e}'
        }), 400

def save_patient_data(name, age, gender, phone, symptoms, diagnosis):
    # Create a dictionary with patient data
    patient_data = {
        'Name': [name],
        'Age': [age],
        'Gender': [gender],
        'Phone': [phone],
        'Symptoms': [symptoms],
        'Diagnosis': [diagnosis],
        'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }
    
    try:
        # Try to read existing Excel file
        existing_df = pd.read_excel('data.xlsx')
        # Create new dataframe with current patient data
        new_df = pd.DataFrame(patient_data)
        # Concatenate existing and new data
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        # If file doesn't exist, create new dataframe
        updated_df = pd.DataFrame(patient_data)
    
    # Save to Excel file
    updated_df.to_excel('data.xlsx', index=False)
    return True

@app.route('/get_recommendations/<recommendation_type>')
def get_recommendations(recommendation_type):
    try:
        # Read user data from Excel
        file_path = os.path.join('reports', 'dataentry.xlsx')
        personal_df = pd.read_excel(file_path, sheet_name='Personal Info')
        health_df = pd.read_excel(file_path, sheet_name='Health Metrics')
        test_df = pd.read_excel(file_path, sheet_name='Test Reports')
        lifestyle_df = pd.read_excel(file_path, sheet_name='Lifestyle Info')

        # Get the latest entry for each dataframe
        latest_personal = personal_df.iloc[-1]
        latest_health = health_df.iloc[-1]
        latest_test = test_df.iloc[-1]
        latest_lifestyle = lifestyle_df.iloc[-1]

        # Create user profile for AI
        user_profile = f"""
        Patient Profile:
        - Age: {latest_personal['Age']}
        - Gender: {latest_personal['Gender']}
        - BMI: {latest_health['BMI']:.1f}
        - Blood Pressure: {latest_health['Blood Pressure']}
        - Activity Level: {latest_lifestyle['Activity Level']}
        - Diet Preferences: {latest_lifestyle['Diet Preferences']}
        - Fasting Blood Glucose: {latest_test['Fasting Blood Glucose']}
        - Post Prandial Glucose: {latest_test['Post Prandial Glucose']}
        - HbA1c: {latest_test['HbA1c']}
        """

        if recommendation_type == 'nutrition':
            prompt = f"""
            Based on this diabetic patient's profile:
            {user_profile}

            Please create a detailed but concise nutrition recommendation plan that includes:
            1. Daily caloric intake
            2. Macro distribution (carbs, protein, fat)
            3. Specific food recommendations
            4. Meal timing suggestions
            5. Foods to avoid
            
            Format the response in clear sections with bullet points.
            """
        else:  # exercise
            prompt = f"""
            Based on this diabetic patient's profile:
            {user_profile}

            Please create a safe and effective exercise plan that includes:
            1. Types of recommended exercises
            2. Weekly schedule
            3. Duration and intensity
            4. Safety precautions
            5. Progress tracking tips
            
            Format the response in clear sections with bullet points.
            """

        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'recommendations': response.text
        })

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    if not os.path.exists('reports'):
        os.makedirs('reports')
    app.run(debug=True, port=5001) 