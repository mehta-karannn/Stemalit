import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3
import io

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
        image_data BLOB,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
connection.commit()

st.sidebar.title('Navigation')
st.info("👈 Click the arrow in the top-left corner to open the sidebar menu.")

app_mode = st.sidebar.radio("Choose Mode", ['User Form', 'Admin Console'])

# --------------------- USER FORM ---------------------
if app_mode == 'User Form':
    st.title("Hello, User!")

    names = st.text_input('Enter your name:')

    if names.strip() != "":
        st.write(f'Hi {names}')
        age = st.slider('Enter your age:', 0, 100, 18)
        st.write(f"Age: {age}")

        if age > 18:
            uploaded_file = st.file_uploader("Upload your Image", type=["png", "jpeg", "jpg"])

            if uploaded_file is not None:
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Uploaded Image", use_column_width=True)

                cursor.execute(
                    "INSERT INTO users (name, age, image_filename, image_data) VALUES (?, ?, ?, ?)",
                    (names, age, uploaded_file.name, image_bytes)
                )
                connection.commit()

                st.success("Your data has been saved!")
            else:
                st.warning("Please upload an image to proceed.")
        else:
            st.info("You must be above 18 to proceed.")
    else:
        st.info('Please enter your name to continue.')

# --------------------- ADMIN CONSOLE ---------------------
elif app_mode == "Admin Console":
    st.title("🔐 Admin Console")

    admin_pass = st.text_input("Enter Admin Password", type="password")

    if admin_pass == "admin123":
        st.success("Access Granted")

        df_all = pd.read_sql_query("SELECT * FROM users", connection)
        st.subheader("📋 All Registered Users")
        st.dataframe(df_all)

        # Show image by selecting unique row (id or timestamp recommended)
        if not df_all.empty:
            df_all['user_id'] = df_all['id'].astype(str) + " | " + df_all['name']
            selected_row = st.selectbox("Select a user entry:", df_all['user_id'].tolist())

            selected_id = int(selected_row.split(" | ")[0])
            cursor.execute("SELECT image_filename, image_data FROM users WHERE id = ?", (selected_id,))
            result = cursor.fetchone()

            if result and result[1]:
                image = Image.open(io.BytesIO(result[1]))
                st.image(image, caption=result[0], use_column_width=True)
            else:
                st.warning("No image available for this user.")
        else:
            st.info("No user data found.")

        if st.button("Export as CSV"):
            df_all.drop(columns="image_data").to_csv("all_users.csv", index=False)
            st.success("Data exported as CSV (check project folder).")

    elif admin_pass:
        st.error("❌ Incorrect Password")
