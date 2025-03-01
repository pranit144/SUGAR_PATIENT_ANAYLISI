from flask import Flask, request, render_template, redirect
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the entered credentials
        entered_email = request.form['email']
        entered_password = request.form['password']
        
        try:
            # Load the Excel file
            df = pd.read_excel('asep_signup/credentials.xlsx')
            
            # Print debug information
            print("\n=== Login Attempt ===")
            print(f"Entered Email: {entered_email}")
            print(f"Entered Password: {entered_password}")
            print("\n=== Stored Credentials ===")
            print(df)
            
            # Simple row check
            for index, row in df.iterrows():
                stored_email = str(row['email'])
                stored_password = str(row['password'])
                
                print(f"\nChecking row {index}:")
                print(f"Comparing {entered_email} with {stored_email}")
                print(f"Comparing {entered_password} with {stored_password}")
                
                if entered_email == stored_email and entered_password == stored_password:
                    print("Match found!")
                    return "Login successful!"
            
            print("No match found")
            return "Invalid credentials"
            
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {str(e)}"
    
    return render_template('login.html')

if __name__ == '__main__':
    # Print credentials file contents at startup
    try:
        df = pd.read_excel('asep_signup/credentials.xlsx')
        print("\nCredentials file contents:")
        print(df)
    except Exception as e:
        print(f"Error reading credentials file: {e}")
    
    app.run(debug=True, port=5004)
