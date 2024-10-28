# MyStock Backend

This is the backend for the MyStock application, built with Flask. The backend manages user authentication, portfolio management, and interaction with stock data.

## Setup Instructions

Follow the steps below to set up and run the backend locally.

### 1. Clone the Repository

First, clone the repository to your local machine:

- **`git clone git@github.com:YourUser/MyStock-Backend.git`**
- **`cd MyStock-Backend`**

### 2. Create a Virtual Environment and Install Dependencies

Set up a virtual environment and install the necessary Python packages from the `requirements.txt` file:

- **`python3 -m venv .venv`**
- **`source .venv/bin/activate`**
- **`pip install -r requirements.txt`**

### 3. Set Up Environment Variables

You need to configure environment variables like the MongoDB connection string. To do this:

1. Copy the `.env.example` file to create your own `.env` file:
   - **`cp .env.example .env`**

2. Open the `.env` file and replace the placeholders (`<username>`, `<password>`, `<dbname>`) with your actual MongoDB credentials and other environment-specific values.

#### Example `.env` File:

MONGODB_URI=mongodb+srv://myusername
@cluster0.mongodb.net/mydatabase?retryWrites=true&w=majority SECRET_KEY=my-secret-key


### 4. Run the Application

Start the Flask development server:

- **`flask run`**

The application will now be running locally. You can access it by navigating to `http://127.0.0.1:5000/` in your browser.

## Contributing

Feel free to open issues and submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

**All rights reserved for Roy Barak**
