from flask import Flask, request, render_template, redirect
import pandas as pd
import os
from pathlib import Path

app = Flask(__name__)

# Create path for asep_signup folder in current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNUP_DIR =  'asep_signup'
EXCEL_FILE = 'credentials.xlsx'

def create_credentials_file():
    try:
        # Create asep_signup directory if it doesn't exist
        os.makedirs(SIGNUP_DIR, exist_ok=True)
        print(f"Directory created/verified at: {SIGNUP_DIR}")
        
        if not os.path.exists(EXCEL_FILE):
            df = pd.DataFrame(columns=['name', 'email', 'password', 'confirm_password'])
            df.to_excel(EXCEL_FILE, index=False)
            print(f"Created new credentials file at: {EXCEL_FILE}")
    except Exception as e:
        print(f"Error creating credentials file: {e}")

@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            print(f"Attempting to save - Name: {name}, Email: {email}")

            # Prepare the new data
            new_data = {
                'name': [name],
                'email': [email],
                'password': [password],
                'confirm_password': [confirm_password]
            }

            # Create DataFrame for new entry
            new_entry = pd.DataFrame(new_data)

            try:
                # If file exists, read and append
                if os.path.exists(EXCEL_FILE):
                    existing_df = pd.read_excel(EXCEL_FILE)
                    updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
                else:
                    # If file doesn't exist, create new
                    updated_df = new_entry

                # Save to Excel
                updated_df.to_excel(EXCEL_FILE, index=False)
                print(f"Data saved successfully to {EXCEL_FILE}")
                print("Current contents of file:")
                print(pd.read_excel(EXCEL_FILE))
                
                return redirect('http://127.0.0.1:5004/')

            except Exception as e:
                print(f"Error saving to Excel: {e}")
                return f"Error saving data: {str(e)}"

        except Exception as e:
            print(f"Error processing form data: {e}")
            return str(e)

    return render_template('signup.html')

if __name__ == '__main__':
    # Create the credentials file at startup
    create_credentials_file()
    
    # Print the current contents of the file
    if os.path.exists(EXCEL_FILE):
        print("Current contents of credentials.xlsx:")
        print(pd.read_excel(EXCEL_FILE))
    else:
        print("credentials.xlsx does not exist yet")
    
    print(f"Server starting. Excel file location: {EXCEL_FILE}")
    app.run(debug=True, port=5006)
