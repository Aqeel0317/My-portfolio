import openpyxl
from flask import Flask, request, render_template, url_for # Added url_for just in case
from collections import defaultdict
from datetime import datetime

# Assuming 'app' is your Flask app instance
# app = Flask(__name__)

# Define the path to your Excel file
students_file = 'path/to/your/students_data.xlsx' # <--- *** IMPORTANT: Update this path ***

# Define the desired grade order and create a sort key
grade_order = ["PG", "NUR", "PREP", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
grade_sort_key = {grade: i for i, grade in enumerate(grade_order)}

def parse_date(date_str):
    """Helper function to parse date strings, returns None if invalid."""
    if not date_str:
        return None
    try:
        # Adjust the format ('%Y-%m-%d') if your dates are stored differently
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Warning: Invalid date format found: {date_str}")
        return None

@app.route('/fee_collection', methods=['GET'])
def fee_collection():
    """
    Displays individual fee payment records, filterable by date range and grade.
    """
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    grade_filter = request.args.get('grade', '').strip()

    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    # List to store individual payment records
    all_payments = []
    all_grades_in_sheet = set() # To populate the grade filter dropdown

    try:
        wb = openpyxl.load_workbook(students_file, data_only=True)
        ws = wb.active
    except FileNotFoundError:
        return "Error: Students data file not found.", 500
    except Exception as e:
        return f"Error opening or reading Excel file: {e}", 500

    # --- Data Processing: Collect individual payments ---
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            student_grade = str(row[4]).strip() if row[4] is not None else ''
            if not student_grade:
                continue # Skip rows without a grade

            # Collect all unique grades found BEFORE filtering for the dropdown
            all_grades_in_sheet.add(student_grade)

            # Apply grade filter if active
            if grade_filter and student_grade != grade_filter:
                continue

            # Get fee for this student
            monthly_fee_raw = row[5]
            monthly_fee = 0.0
            if isinstance(monthly_fee_raw, (int, float)):
                monthly_fee = float(monthly_fee_raw)
            elif isinstance(monthly_fee_raw, str) and monthly_fee_raw.strip():
                 try:
                     monthly_fee = float(monthly_fee_raw.strip())
                 except ValueError:
                     print(f"Warning: Skipping invalid fee '{monthly_fee_raw}' in row {row_idx}.")
                     # Decide if you want to skip the whole row or just treat fee as 0
                     continue # Skip row if fee is invalid text

            paid_dates_str = str(row[9]).strip() if row[9] is not None else ''
            paid_dates = [d.strip() for d in paid_dates_str.split(",") if d.strip()]
            student_identifier = str(row[1]).strip() if row[1] is not None else f"Row {row_idx}"

            # Create a separate record for each valid payment date
            for date_str in paid_dates:
                paid_date = parse_date(date_str)
                if not paid_date:
                    continue # Skip invalid dates

                # Apply date range filtering
                if start_date and paid_date < start_date:
                    continue
                if end_date and paid_date > end_date:
                    continue

                # Add individual payment record
                all_payments.append({
                    'grade': student_grade,
                    'date': date_str,          # String date for display
                    'parsed_date': paid_date,  # Date object for sorting
                    'student': student_identifier,
                    'fee_paid': monthly_fee
                })

        except (IndexError, TypeError, ValueError) as e:
            print(f"Warning: Skipping row {row_idx} due to error: {e}. Row data: {row}")
            continue

    # --- Sort the collected payments ---
    all_payments.sort(key=lambda p: (
        grade_sort_key.get(p['grade'], len(grade_order)), # Sort by grade order
        p['parsed_date'] or datetime.min.date(),          # Then by date
        p['student'].lower()                              # Then by student name (case-insensitive)
    ))

    # --- Prepare list of grades for the filter dropdown ---
    sorted_grades_list = sorted(list(all_grades_in_sheet), key=lambda g: grade_sort_key.get(g, len(grade_order)))

    # --- Calculate Grand Total ---
    grand_total_fee = sum(p['fee_paid'] for p in all_payments)

    return render_template(
        'fee_collection.html',
        all_payments=all_payments,             # Pass the list of individual payments
        all_grades=sorted_grades_list,         # Pass unique grades found in sheet
        start_date=start_date_str,
        end_date=end_date_str,
        grade_filter=grade_filter,
        grand_total_fee=grand_total_fee        # Pass the calculated total
    )

# --- Add basic structure if running this file directly ---
# if __name__ == '__main__':
#     app = Flask(__name__)
#     # Make sure necessary functions/variables are defined or imported
#     # e.g., students_file, grade_order, grade_sort_key, parse_date
#     # app.add_url_rule('/fee_collection', view_func=fee_collection)
#     app.run(debug=True)