from flask import Flask, render_template, jsonify
import google.generativeai as genai
import pandas as pd
import os

app = Flask(__name__)

# Configure Gemini API using your API key (for testing only; use environment variables in production)
gemini_api_key = "AIzaSyC9NwVA01MVc2_zqEZpWLfeoAs_nIR_66M"
genai.configure(api_key=gemini_api_key)

# Define Gemini generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the Gemini model instance
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

def get_latest_data():
    """Read the latest entry from each sheet in the Excel file."""
    file_path = 'dataentry.xlsx'
    personal_df = pd.read_excel(file_path, sheet_name='Personal Info')
    health_df = pd.read_excel(file_path, sheet_name='Health Metrics')
    test_df = pd.read_excel(file_path, sheet_name='Test Reports')
    lifestyle_df = pd.read_excel(file_path, sheet_name='Lifestyle Info')

    latest_personal = personal_df.iloc[-1]
    latest_health = health_df.iloc[-1]
    latest_test = test_df.iloc[-1]
    latest_lifestyle = lifestyle_df.iloc[-1]
    return latest_personal, latest_health, latest_test, latest_lifestyle

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recommendations/<plan_type>')
def get_recommendations(plan_type):
    try:
        # Retrieve the latest patient data
        latest_personal, latest_health, latest_test, latest_lifestyle = get_latest_data()

        # Build the patient profile string
        user_profile = f"""
Patient Profile for Planning:
• Name: {latest_personal['Full Name']}
• Age: {latest_personal['Age']}
• Gender: {latest_personal['Gender']}
• BMI: {latest_health['BMI']:.1f}
• Current Weight: {latest_health['Weight (kg)']} kg
• Blood Pressure: {latest_health['Blood Pressure']}
• Activity Level: {latest_lifestyle['Activity Level']}
• Diet Preferences: {latest_lifestyle.get('Diet Preferences', 'N/A')}
• Latest Blood Sugar Readings:
    – Fasting: {latest_test['Fasting Blood Glucose']} mg/dL
    – Post Prandial: {latest_test['Post Prandial Glucose']} mg/dL
    – HbA1c: {latest_test['HbA1c']}%
        """

        # Define the prompt based on the requested plan type
        if plan_type.lower() == 'nutrition':
            prompt = f"""
Based on this diabetic patient's profile:
{user_profile}

Please create a detailed but concise **Nutrition Plan** that includes:
1. **Daily Caloric Intake Recommendation**
2. **Macro Distribution** (carbohydrates, protein, fat)
3. **Specific Food Recommendations and Meal Ideas**
4. **Meal Timing Suggestions**
5. **Foods to Avoid**
6. **Snack Options for Managing Blood Sugar**
7. **Hydration Recommendations**

Format your response using clear headings, bullet lists, and proper line breaks.
            """
        elif plan_type.lower() == 'exercise':
            prompt = f"""
Based on this diabetic patient's profile:
{user_profile}

Please create a safe and effective **Exercise Plan** that includes:
1. **Types of Recommended Exercises** (cardio and strength training)
2. **Weekly Schedule with Rest Days**
3. **Duration and Intensity Recommendations**
4. **Safety Precautions for Diabetic Patients**
5. **Blood Sugar Monitoring Guidelines During Exercise**
6. **Warning Signs to Watch For**
7. **Progress Tracking Suggestions**
8. **Warm-Up and Cool-Down Routines**

Format your response using clear headings, bullet lists, and proper line breaks.
            """
        else:
            return jsonify({'success': False, 'message': 'Invalid recommendation type.'}), 400

        # Generate recommendations using the Gemini model
        response = model.generate_content(prompt)

        return jsonify({
            'success': True,
            'recommendations': response.text
        })

    except Exception as e:
        print(f"Error generating {plan_type} plan: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)