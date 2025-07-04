import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3

# Connect to SQLite database
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        image_filename TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
connection.commit()

# Streamlit UI
st.title("Hello, User!")

names = st.text_input('Enter your name:')

if names.strip() != "":
    st.write(f'Hi {names}')
    age = st.slider('Enter your age:', 0, 100, 18)
    st.write(f"Age: {age}")

    if age > 18:
        uploaded_file = st.file_uploader("Upload your Image", type=["png", "jpeg", "jpg"])

        if uploaded_file is not None:
            # Display the image (but don't save it)
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            
            cursor.execute(
                "INSERT INTO users (name, age, image_filename) VALUES (?, ?, ?)",
                (names, age, uploaded_file.name)
            )
            connection.commit()

            st.success("Your data has been saved!")
        else:
            st.warning("Please upload an image to proceed.")
    else:
        st.info("You must be above 18 to proceed.")
else:
    st.info('Please enter your name to continue.')
