
# Student Management and Fee Collection System

This is a Flask-based web application designed to manage student records, track fee payments, and generate reports. The system uses an Excel file (`.xlsx`) as its database, making it lightweight and easy to manage without a separate database server.

-----

## Features ✨

  * **Student Management**: Add, modify, and delete student records.
  * **Fee Tracking**: Record various types of fees including monthly fees, admission fees, annual charges, and exam charges.
  * **Payment History**: Track payments by month and date.
  * **Dues Calculation**: Automatically calculates outstanding dues for each student.
  * **Student Picture Integration**: Upload and display student pictures linked to their records.
  * **Search & Filter**: Easily search for students by ID, name, or father's name. Filter students by grade, dues range, or sort by grade and dues.
  * **Detailed Student Reports**: Generate a comprehensive report for each student, including a summary of fees, dues, and a history of monthly payments.
  * **Fee Collection Report**: View a filtered report of collected fees based on date, grade, or month.
  * **Excel as Database**: All data is stored in a single, human-readable `students.xlsx` file.

-----

## Prerequisites ⚙️

  * **Python 3.6+**
  * **Pip** (Python package installer)

-----

## Setup and Installation 🚀

1.  **Save the code**: Save the provided Python code as `app.py`.

2.  **Create a virtual environment**: This is a best practice to manage project dependencies.

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:

      * **On Windows**:
        ```bash
        venv\Scripts\activate
        ```
      * **On macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required libraries**:

    ```bash
    pip install Flask openpyxl werkzeug
    ```

5.  **Create the necessary directories**: The application expects a `data` directory and a `static/uploads` directory to exist. The `app.py` script automatically creates these if they don't already.

      * `data/`: Stores the `students.xlsx` file.
      * `static/uploads/`: Stores student pictures.

6.  **Create the templates**: You need to create the HTML files in a `templates` folder with the following names:

      * `index.html`
      * `add_student.html`
      * `students.html`
      * `test.html` (Used for the modify student page)
      * `student_report1.html`
      * `fee_collection.html`

    *Note: The HTML content for these templates is not included in the provided Python code. You will need to create them based on the routes in `app.py`.*

7.  **Run the application**:

    ```bash
    python app.py
    ```

8.  **Access the application**: Open your web browser and go to `http://127.0.0.1:5000`.

-----

## Usage Guide 📖

### **Adding a New Student**

Navigate to the "Add Student" page. Fill out the student details in the form, including an ID, name, fee information, and optional picture. The application automatically calculates initial dues and saves the data to the Excel file.

### **Managing Students**

The main "Students" page lists all students. You can use the search bar to find students by ID, name, or father's name. The filtering options allow you to view students by specific grade levels, or those with dues in a certain range. The table provides a quick overview of each student's current fee status.

### **Modifying a Student's Record**

Click the "Modify" button next to a student's name on the manage students page. The form will pre-populate with the student's existing data. You can update any field, add or remove paid months, and upload a new picture. The dues will be recalculated automatically upon saving.

### **Deleting a Student**

On the manage students page, you can delete a student's record. This action permanently removes their entry from the Excel file and also deletes their associated picture from the server.

### **Viewing a Student Report**

Clicking the "Report" button provides a detailed summary for a single student, including all fees, payments, dues, and a history of all monthly payments. You can also add and save remarks on this page.

### **Fee Collection Report**

The "Fee Collection" page allows you to generate a report on collected fees. You can filter this report by a date range, grade, or specific month to get a summary of payments.

-----

## File Structure 📂

The application requires a specific folder structure to work correctly:

```
.
├── app.py
├── data/
│   └── students.xlsx
├── static/
│   ├── css/
│   │   └── style.css  (Optional, for styling)
│   └── uploads/
│       └── <student_pictures>.<ext>
└── templates/
    ├── index.html
    ├── add_student.html
    ├── students.html
    ├── test.html
    ├── student_report1.html
    └── fee_collection.html
```