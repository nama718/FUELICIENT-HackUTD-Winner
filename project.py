# Project FUELICIENT
# Authors: Isaac Philo, Aman Balam, Adrian Alvarez, Sriram Lakamsani

import streamlit as st
import pyrebase
from lib.main import *

def prepare_authentication():
    firebaseConfig = {
      'apiKey': "AIzaSyDE8sw9kKp5Pr8WdKo-wKrukogbAefEEOY",
      'authDomain': "fuelicient.firebaseapp.com",
      'projectId': "fuelicient",
      'storageBucket': "fuelicient.firebasestorage.app",
      'messagingSenderId': "322091244296",
      'appId': "1:322091244296:web:b1e2997defb4364f852abd",
      'measurementId': "G-BTKNF9CYJ7",
      "databaseURL": "https://console.firebase.google.com/project/fuelicient/database/fuelicient-default-rtdb/data/~2F"
      
    }
    st.session_state.firebase = pyrebase.initialize_app(firebaseConfig)
    return st.session_state.firebase.auth()

def authenticate(auth, email, password):
    print(f"Beginning authentication with email = {email} and password = {password}")
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.session_state['signin'] = user
        st.session_state.email = user['email']
        st.session_state.auth = auth
        print("User created")
        return True
    except Exception as e1:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['signin'] = user
            st.session_state.email = user['email']
            st.session_state.auth = auth
            print("User logged in")
            print(e1)
            return True
        except Exception as e2:
            st.session_state.pop('signin', None)
            st.session_state.pop('email', None)
            st.session_state.pop('auth', None)
            print("Login failed")
            print(e2)
            st.write("Password invalid!")
            return False

# This will allow for the user to either log in or create an account, in the same interface
def login():
    print("About to log in")
    auth = prepare_authentication()
    st.markdown("## Log into or create your account:")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password") # try "example"
    if st.button("Enter"):
        if "signin" not in st.session_state:
            print("About to authenticate")
            if authenticate(auth, email, password):
                print("About to rerun")
                st.rerun()

# Everything that should happen after the login has occurred
def post_login():
    print("Post login")
    with st.sidebar:
        st.write(f"Signed in as {st.session_state.signin['email']}") # By this point, the user is guaranteed to be signed in.
        if st.button("Logout"):
            st.session_state.auth.current_user = None
            st.session_state.pop('signin', None)
            st.session_state.pop('email', None)
            st.session_state.pop('auth', None)
            st.rerun()
    main() # Call the visualization code from the other file
    
#    if st.button("Add new note..."):
#        add_new_note()
    
#Main code begins here
st.set_page_config(page_title="FUELICIENT", page_icon="FUELICIENT logo.jpg", layout="centered", initial_sidebar_state="auto", menu_items=None)
load_dotenv()
st.markdown("<h1 style='text-align: center; color: black;'>FUELICIENT</h1>", unsafe_allow_html=True)
st.markdown("""---""")

if "signin" not in st.session_state:
    login()

if "signin" in st.session_state:
    post_login()