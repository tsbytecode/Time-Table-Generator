# Timetable Generator

This project is a web-based application for generating school timetables. It consists of a Flask frontend and a Go backend that handles the core timetable generation logic.

## Project Purpose

The Timetable Generator is designed to simplify the complex task of creating and managing school timetables. It provides a user-friendly interface for administrators and educators to:

-   **Automate Timetable Creation:**  Leverage the Go-based backend to automatically generate optimized timetables, saving time and reducing manual effort.
-   **Customize Timetables:**  Manually create or edit timetables to meet specific requirements.
-   **Manage User Access:**  Securely manage user accounts with features like registration, login, and password reset.
-   **Import and Export Data:**  Easily import existing timetable data and export generated timetables in CSV format for offline use.

## Features

-   User authentication (login, registration, password reset)
-   Manual and automatic timetable creation
-   Import/export timetables as CSV files
-   Database integration for storing user and timetable data

## Project Structure

-   `Timetable_Generator_v2.0/`: Contains the main application.
    -   `app.py`: The Flask web application.
    -   `algo/`: Contains the Go service for timetable generation.
        -   `main.go`: The main Go service file.
        -   `algo/algo.go`: The core timetable generation logic.
    -   `static/`: Static files (CSS, JavaScript).
    -   `templates/`: HTML templates for the Flask application.
    -   `users.db`: SQLite database for user data.
    -   `x.db`: SQLite database for timetable data.

## Setup and Installation

### Prerequisites

-   Python 3.6+
-   Go 1.15+

### Backend (Go Service)

1.  **Navigate to the \`algo\` directory:**
    \`\`\`bash
    cd Timetable_Generator_v2.0/algo
    \`\`\`

2.  **Install dependencies:**
    \`\`\`bash
    go mod tidy
    \`\`\`

3.  **Run the service:**
    \`\`\`bash
    go run main.go
    \`\`\`
    The Go service will start on \`http://localhost:8080\`.

### Frontend (Flask Application)

1.  **Navigate to the \`Timetable_Generator_v2.0\` directory:**
    \`\`\`bash
    cd Timetable_Generator_v2.0
    \`\`\`

2.  **Install Python dependencies:**
    *(Note: A \`requirements.txt\` file is not provided. You will need to install the following dependencies manually.)*
    \`\`\`bash
    pip install Flask
    pip install requests
    \`\`\`

3.  **Run the Flask application:**
    \`\`\`bash
    python app.py
    \`\`\`
    The Flask application will start on \`http://localhost:5005\`.

## Usage

1.  **Start the Go service** as described in the "Backend (Go Service)" section.
2.  **Start the Flask application** as described in the "Frontend (Flask Application)" section.
3.  **Open your web browser** and navigate to \`http://localhost:5005\`.
4.  **Register a new user** by clicking the "Register" link and filling out the registration form.
5.  **Log in** with your newly created credentials.
6.  Once logged in, you will be directed to the main dashboard, where you can:
    -   **Create a timetable automatically:**  Click the "Automatic" button and let the generator create a timetable for you.
    -   **Create a timetable manually:**  Click the "Manual" button and fill in the timetable slots yourself.
    -   **View existing timetables:**  See a list of your saved timetables.
    -   **Export a timetable:**  Download a timetable in CSV format.
    -   **Import a timetable:**  Upload a timetable from a CSV file.
