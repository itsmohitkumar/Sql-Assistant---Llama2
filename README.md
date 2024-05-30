# SQL Assistant 🦙

Welcome to SQL Assistant, a Streamlit application that assists you in querying data from a MySQL database.

## Overview

SQL Assistant is a conversational interface that allows users to interactively query a MySQL database containing pizza order data. It provides a user-friendly interface for asking questions about the data and receiving informative responses.

## Features

- Connects to a MySQL database to fetch pizza order data.
- Utilizes a Conversational Retrieval Chain to provide conversational responses to user queries.
- Supports interactive chatting with the SQL Assistant.
- Displays column names and sample data from the database.
- Allows users to ask questions about the pizza order data.

## Setup

#1. Clone the repository:

   ```bash
   git clone https://github.com/itsmohitkumar/Sql-Assistant---Llama2.git
   cd sql-assistant
   ```

#2. Install dependencies:

bash
```bash
pip install -r requirements.txt
```

#3. Run the application:

```bash
streamlit run main.py
```

#4. Open your web browser and go to http://localhost:8501 to access the SQL Assistant.

## Requirements
Ensure you have the following dependencies installed:

- Python 3.6+
- MySQL Server
- Streamlit
- HuggingFace Transformers
- MySQL Connector
- LangChain Community

## Usage
1. Input your MySQL database connection details.
2. Run `streamlit run app.py` to start the Streamlit application.
3. Interact with the SQL Assistant by asking questions about the data.

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.
