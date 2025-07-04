import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3
st.set_page_config(page_title="User/Admin App", layout="wide")
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


st.sidebar.title('Navigation')
st.info("👈 Click the arrow in the top-left corner to open the sidebar menu.")

app_mode=st.sidebar.radio("Choose Mode",['User Form','Admin Console'])
if app_mode=='User Form':
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


# ---Admin Acess---
elif app_mode == "Admin Console":
    st.title("🔐 Admin Console")

    admin_pass = st.text_input("Enter Admin Password", type="password")

    if admin_pass == "admin123":  # replace with st.secrets in production
        st.success("Access Granted")

        df_all = pd.read_sql_query("SELECT * FROM users", connection)
        st.subheader("📋 All Registered Users")
        st.dataframe(df_all)

        # Optional: Export
        if st.button("Export as CSV"):
            df_all.to_csv("all_users.csv", index=False)
            st.success("Data exported as CSV (check project folder).")

    elif admin_pass:
        st.error("❌ Incorrect Password")
