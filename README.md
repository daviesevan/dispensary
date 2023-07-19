# Dispensary
Sure! Here's an example README file that you can include in your repository to provide information about your Flask application:

---

# Dispensary Management System

This is a web application developed using Flask, a Python web framework. The Dispensary Management System allows patients to register for appointments and doctors to manage patient records.

## Features

- User registration and login
- Patient appointment booking
- Doctor dashboard to manage patient records
- Password reset functionality

## Installation

1. Clone the repository to your local machine:
   ```shell
   git clone https://github.com/daviesevan/dispensary.git
   ```

2. Change into the project directory:
   ```shell
   cd dispensary
   ```

3. Create a virtual environment:
   ```shell
   python -m venv venv
   ```

4. Activate the virtual environment:
   - For Windows:
     ```shell
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```shell
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```shell
   pip install -r requirements.txt
   ```

6. Set up the environment variables:
   - Create a `.env` file in the project root directory.
   - Add the following environment variables to the `.env` file:
     ```dotenv
     MAIL_USERNAME=your-email@example.com
     MAIL_PASSWORD=your-email-password
     SECRET_KEY=your-secret-key
     ```

7. Initialize the database:
   ```shell
   flask db init
   flask db migrate
   flask db upgrade
   ```

8. Run the application:
   ```shell
   flask run
   ```

9. Open your web browser and visit `http://localhost:5000` to access the application.

## Usage

- Register a new account as a patient or doctor.
- Log in using your credentials.
- Patients can book appointments and view their details.
- Doctors can manage patient records and appointments.
- Forgot password functionality is available to reset your password.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, feel free to open a GitHub issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---
