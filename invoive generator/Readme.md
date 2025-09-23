# Flask-based Invoice Management System 🧾

This application is a simple, yet robust, web-based tool for generating and managing invoices. Built with **Python** and **Flask**, it allows users to input customer and invoice details through a web form and then automatically generates a **PDF** invoice. The system also saves all data to a local **Excel file** for record-keeping and data management.


## Features ✨

  * **Invoice Generation**: Create professional-looking invoices with a user-friendly web form.
  * **PDF Output**: Automatically generates a PDF file of the invoice using `pdfkit` for easy sharing and printing.
  * **Data Persistence**: All invoice and customer information is saved to an `invoices.xlsx` file, ensuring a permanent record of all transactions.
  * **Dynamic Forms**: The application's forms are built with Flask-WTF, providing security and validation.
  * **Local & Portable**: Designed to be run locally, making it a great tool for small businesses or personal use. The use of PyInstaller and `resource_path` ensures it can be bundled into a standalone executable.

-----

## Technology Stack 🛠️

  * **Backend**: Python, Flask
  * **Frontend**: HTML, CSS, JavaScript (minimal)
  * **Data Storage**: Microsoft Excel (`.xlsx` format)
  * **PDF Generation**: `pdfkit`, `wkhtmltopdf`
  * **Form Handling**: `Flask-WTF`, `WTForms`
  * **Excel Integration**: `openpyxl`

-----

## Prerequisites ⚙️

  * **Python 3.6+**
  * **wkhtmltopdf**: A standalone command-line tool used by `pdfkit` to render HTML to PDF. The application is configured to look for it within a bundled `wkhtmltopdf` folder, but you may need to install it manually if you run from source.
      * **Windows**: The code is configured to use a bundled `.exe` file.
      * **macOS**: `brew install wkhtmltopdf`
      * **Linux (Ubuntu)**: `sudo apt-get install wkhtmltopdf`

-----

## Setup and Installation 🚀

1.  **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment** (highly recommended):

    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install the required Python packages**:

    ```bash
    pip install Flask Flask-WTF openpyxl pdfkit
    ```

4.  **(Optional) Set up `wkhtmltopdf`**:
    The provided code is set up for PyInstaller bundling, but if you're running the Flask app directly, ensure that `wkhtmltopdf` is installed and its path is correctly configured in your system's environment variables or updated within the `app.py` file.

5.  **Run the application**:

    ```bash
    python app.py
    ```

    The application will automatically open in your default web browser.

-----

## Usage Guide 📋

1.  **Access the Form**: Open your browser and go to `http://127.0.0.1:5000`. You will be greeted with the invoice creation form.
2.  **Enter Details**: Fill in the customer information and the details for each product or service. The form includes fields for quantity, brand, model, details, and amount.
3.  **Calculate Totals**: The form automatically handles calculations for taxes, discounts, and the final grand total.
4.  **Generate Invoice**: Click **"Save and Generate Invoice"**. The data will be saved to `invoices.xlsx`, and a PDF invoice will be generated and saved in the `pdfs` folder. The application will also display the rendered HTML version of the invoice in your browser.
5.  **Manage Data**: The `invoices.xlsx` file will contain three sheets:
      * `students`: Stores customer details.
      * `Invoices`: Contains summary information for each invoice.
      * `InvoiceDetails`: Records the line-item details for each invoice.

## Troubleshooting 🐛

  * **`pdfkit.from_string(...)` fails**: This is most likely due to an issue with `wkhtmltopdf`. Ensure it is installed correctly and that the path in `app.py` is pointing to the correct executable.
  * **"CSRF token missing" error**: Make sure your form in `add_invoice_item.html` includes `{{ form.csrf_token }}`. Flask-WTF requires this for security.
  * **Permissions Errors**: If the application cannot create the `invoices.xlsx` or `pdfs` directories, check that the script has the necessary write permissions in the directory where it's being run.