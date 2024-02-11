# Project Name

Automated Data Creation for Bahmni, OpenMRS, and Odoo using FastAPI

## Overview

This Python project leverages FastAPI to automate the creation of concepts, products, and drugs in Bahmni, OpenMRS, and Odoo. The application reads data from a CSV file, uploads it to both OpenMRS and Odoo APIs, and performs duplicate checks to ensure data integrity.

## Features

- **Concept Creation:** Automatically create concepts in Bahmni based on the data provided in the CSV file.
- **Product Creation:** Create products in Odoo using the information parsed from the CSV file.
- **Drug Creation:** Add drug entries in OpenMRS by uploading data from the CSV file.
- **Duplicate Checks:** Ensure data consistency by checking for duplicates before uploading to both OpenMRS and Odoo APIs.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-project.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Open the `config.py` file and provide the necessary API endpoint URLs, credentials, and other configuration details for OpenMRS and Odoo.

2. Ensure that the CSV file containing data to be uploaded is in the project directory.

## Usage

1. Run the FastAPI application:

   ```bash
   uvicorn main:app --reload
   ```

2. Access the FastAPI documentation to understand the available endpoints and how to use them:

   ```bash
   http://127.0.0.1:8000/docs
   ```

```

## Contribution Guidelines

Feel free to contribute by submitting bug reports, feature requests, or pull requests. Please adhere to the project's coding style and guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
