from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os
import os
import threading
import webview

app = Flask(__name__)

# Path to the Excel file
file_path = 'data/transport_data.xlsx'

# Function to create an Excel file if it doesn't exist
def load_data():
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["Student Name", "Father's Name", "Contact", "Location", "Grade", "Monthly Charges", "Month", "Paid Charges", "Paid Date", "Dues"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
    else:
        df = pd.read_excel(file_path)
    return df

# Home page that displays student list with total paid and unpaid charges
@app.route('/', methods=["GET", "POST"])
def index():
    df = load_data()
    
    # Get search query from form if any
    search_query = request.args.get('search', '')
    
    # Filter the dataframe if there is a search query
    if search_query:
        df = df[df['Student Name'].str.contains(search_query, case=False, na=False)]
    
    # Group by Student Name and aggregate
    student_grouped = df.groupby('Student Name').agg({
        'Father\'s Name': 'first',
        'Contact': 'first',
        'Location': 'first',
        'Grade': 'first',
        'Monthly Charges': 'sum',
        'Paid Charges': 'sum',
        'Dues': 'sum',
        'Month': 'first',
    }).reset_index()
    
    # Calculate total paid and unpaid charges for display
    total_paid = student_grouped['Paid Charges'].sum()
    total_unpaid = student_grouped['Dues'].sum()

    return render_template('transport.html', students=student_grouped.to_dict(orient='records'), total_paid=total_paid, total_unpaid=total_unpaid, search_query=search_query)

def start_flask():
    app.run(host='127.0.0.1', port=5000)


# Add student page
@app.route('/add_student', methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_name = request.form['student_name']
        father_name = request.form['father_name']
        contact = request.form['contact']
        location = request.form['location']
        grade = request.form['grade']
        monthly_charges = request.form['monthly_charges']
        month = request.form['month']
        paid_charges = request.form['paid_charges']
        paid_date = request.form['paid_date']
        joining_date = request.form['joining_date']  # New joining date field
        dues = float(monthly_charges) - float(paid_charges)

        new_data = {
            "Student Name": student_name,
            "Father's Name": father_name,
            "Contact": contact,
            "Location": location,
            "Grade": grade,
            "Monthly Charges": monthly_charges,
            "Month": month,
            "Paid Charges": paid_charges,
            "Paid Date": paid_date,
            "Joining Date": joining_date,  # Save joining date
            "Dues": dues,
        }

        df = load_data()
        new_row = pd.DataFrame([new_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(file_path, index=False)

        return redirect(url_for('index'))

    return render_template('trs.html')

# Delete student route
@app.route('/delete_student/<student_name>', methods=["POST"])
def delete_student(student_name):
    df = load_data()

    # Remove student records based on Student Name
    df = df[df['Student Name'] != student_name]

    # Save the updated DataFrame back to the Excel file
    df.to_excel(file_path, index=False)

    return redirect(url_for('index'))

# Route to view a student's full report
@app.route('/report/<student_name>')
def student_report(student_name):
    df = load_data()

    # Filter the records for the selected student
    student_data = df[df['Student Name'] == student_name]
    return render_template('transport_report.html', student_name=student_name, student_data=student_data.to_dict(orient='records'))


# Update charges page
@app.route('/update_charges/<int:student_id>', methods=["GET", "POST"])
def update_charges(student_id):
    df = load_data()
    student_data = df.iloc[student_id]
    
    if request.method == "POST":
        if "next_month" in request.form:
            new_data = {
                "Student Name": student_data["Student Name"],
                "Father's Name": student_data["Father's Name"],
                "Contact": student_data["Contact"],
                "Location": student_data["Location"],
                "Grade": student_data["Grade"],
                "Monthly Charges": request.form['monthly_charges'],
                "Month": request.form['month'],
                "Paid Charges": request.form['paid_charges'],
                "Paid Date": request.form['paid_date'],
                "Dues": float(request.form['monthly_charges']) - float(request.form['paid_charges']),
            }

            df = load_data()
            next_month_data = pd.DataFrame([new_data])
            df = pd.concat([df, next_month_data], ignore_index=True)
            df.to_excel(file_path, index=False)
            return redirect(url_for('index'))

        new_monthly_charges = request.form['monthly_charges']
        new_paid_charges = request.form['paid_charges']
        new_paid_date = request.form['paid_date']

        df.at[student_id, "Monthly Charges"] = new_monthly_charges
        df.at[student_id, "Paid Charges"] = new_paid_charges
        df.at[student_id, "Paid Date"] = new_paid_date

        dues = float(new_monthly_charges) - float(new_paid_charges)
        df.at[student_id, "Dues"] = dues

        df.to_excel(file_path, index=False)

        return redirect(url_for('index'))

    return render_template('update_charges.html', student=student_data)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Create a webview window
    webview.create_window('School Software', 'http://127.0.0.1:5000')
    webview.start()
