import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Required for non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from flask import Flask, send_file, render_template
import io
import os

app = Flask(__name__)

def create_sample_data():
    """Create a sample Excel file if it doesn't exist"""
    # Create report directory if it doesn't exist
    os.makedirs('report', exist_ok=True)
    
    if not os.path.exists('report/dataentry.xlsx'):  # Changed file path
        # Create sample dates
        dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d %H:%M:%S") for x in range(7)]
        
        # Create sample data
        test_data = {
            'Date Added': dates,
            'Patient Name': ['Test Patient'] * 7,
            'Fasting Blood Glucose': [95, 98, 92, 96, 95, 93, 97],
            'Post Prandial Glucose': [120, 125, 118, 122, 121, 119, 123],
            'HbA1c': [5.7, 5.8, 5.6, 5.7, 5.7, 5.6, 5.8]
        }
        
        # Create DataFrame
        df = pd.DataFrame(test_data)
        
        # Save to Excel in report folder
        with pd.ExcelWriter('report/dataentry.xlsx') as writer:  # Changed file path
            df.to_excel(writer, sheet_name='Test Reports', index=False)
        print("Created sample data file: report/dataentry.xlsx")

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blood Glucose Analysis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                text-align: center;
            }
            img {
                max-width: 100%;
                height: auto;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Blood Glucose Analysis</h1>
        <img src="/generate_graphs" alt="Blood Glucose Graph">
    </body>
    </html>
    '''

@app.route('/generate_graphs')
def generate_graphs():
    try:
        # Read data from Excel file in report folder
        print("Reading report/dataentry.xlsx...")  # Changed file path
        df = pd.read_excel('report/dataentry.xlsx')  # Changed file path
        print("Data loaded:", df)
        
        # Create figure with adjusted size and subplots
        plt.figure(figsize=(12, 8))
        
        # Plot all measurements in one graph
        plt.plot(range(len(df)), df['Fasting Blood Glucose'], 
                marker='o', label='Fasting', color='blue', linewidth=2)
        
        plt.plot(range(len(df)), df['Post Prandial Glucose'], 
                marker='s', label='Post Prandial', color='green', linewidth=2)
        
        # Plot HbA1c without scaling
        plt.plot(range(len(df)), df['HbA1c'],
                marker='^', label='HbA1c', color='red', linewidth=2)
        
        # Calculate and plot estimated blood sugar
        hba1c_glucose = (28.7 * df['HbA1c']) - 46.7
        df['Estimated Blood Sugar'] = (
            (0.3 * df['Fasting Blood Glucose']) +
            (0.5 * df['Post Prandial Glucose']) +
            (0.2 * hba1c_glucose)
        )
        plt.plot(range(len(df)), df['Estimated Blood Sugar'],
                marker='*', label='Estimated Blood Sugar', 
                color='purple', linewidth=2, linestyle='--')
        
        # Customize the plot
        plt.title('Blood Glucose Measurements Over Time', pad=20, fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Values', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Use dates for x-axis if available
        if 'Date Added' in df.columns:
            plt.xticks(range(len(df)), df['Date Added'], rotation=45)
        
        plt.tight_layout()
        
        # Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        print(f"Error generating graph: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/get_statistics')
def get_statistics():
    try:
        # Read the Test Reports sheet from report folder
        df = pd.read_excel('report/dataentry.xlsx', sheet_name='Test Reports')  # Changed file path
        
        # Calculate statistics
        stats = {
            'Fasting Blood Glucose': {
                'Average': df['Fasting Blood Glucose'].mean(),
                'Min': df['Fasting Blood Glucose'].min(),
                'Max': df['Fasting Blood Glucose'].max()
            },
            'Post Prandial Glucose': {
                'Average': df['Post Prandial Glucose'].mean(),
                'Min': df['Post Prandial Glucose'].min(),
                'Max': df['Post Prandial Glucose'].max()
            },
            'HbA1c': {
                'Average': df['HbA1c'].mean(),
                'Min': df['HbA1c'].min(),
                'Max': df['HbA1c'].max()
            }
        }
        
        return stats

    except Exception as e:
        return f"Error calculating statistics: {str(e)}", 500

if __name__ == '__main__':
    create_sample_data()  # Create sample data file if it doesn't exist
    app.run(debug=True, port=5002) 