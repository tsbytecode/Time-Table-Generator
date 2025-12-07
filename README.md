# Timetable Generator

This project is a web-based application for generating school timetables. It consists of a Flask frontend and a Go backend that handles the core timetable generation logic.

## Features

- User authentication (login, registration, password reset)
- Manual and automatic timetable creation
- Import/export timetables as CSV files
- Database integration for storing user and timetable data

## Project Structure

- `Timetable_Generator_v2.0/`: Contains the main application.
  - `app.py`: The Flask web application.
  - `algo/`: Contains the Go service for timetable generation.
    - `main.go`: The main Go service file.
    - `algo/algo.go`: The core timetable generation logic.
  - `static/`: Static files (CSS, JavaScript).
  - `templates/`: HTML templates for the Flask application.
  - `users.db`: SQLite database for user data.
  - `x.db`: SQLite database for timetable data.

## Setup and Installation

### Prerequisites

- Python 3.6+
- Go 1.15+

### Backend (Go Service)

1. **Navigate to the `algo` directory:**
   ```bash
   cd Timetable_Generator_v2.0/algo
   ```

2. **Install dependencies:**
   ```bash
   go mod tidy
   ```

3. **Run the service:**
   ```bash
   go run main.go
   ```
   The Go service will start on `http://localhost:8080`.

### Frontend (Flask Application)

1. **Navigate to the `Timetable_Generator_v2.0` directory:**
   ```bash
   cd Timetable_Generator_v2.0
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: A `requirements.txt` file is not provided. You will need to install the following dependencies manually.)*
   ```bash
   pip install Flask requests
   ```


3. **Run the Flask application:**
   ```bash
   python app.py
   ```
   The Flask application will start on `http://localhost:5005`.

## Usage

1. **Start the Go service** as described above.
2. **Start the Flask application** as described above.
3. **Open your web browser** and navigate to `http://localhost:5005`.
4. **Register a new user** or log in with an existing account.
5. **Create a timetable** either manually or automatically using the provided forms.
6. **View, export, or import** your timetables as needed.
