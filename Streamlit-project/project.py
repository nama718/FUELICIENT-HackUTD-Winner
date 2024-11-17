import streamlit as st
import pyrebase

def prepare_authentication():
    firebaseConfig = {
      'apiKey': "AIzaSyDE8sw9kKp5Pr8WdKo-wKrukogbAefEEOY",
      'authDomain': "fuelicient.firebaseapp.com",
      'projectId': "fuelicient",
      'storageBucket': "fuelicient.firebasestorage.app",
      'messagingSenderId': "322091244296",
      'appId': "1:322091244296:web:b1e2997defb4364f852abd",
      'measurementId': "G-BTKNF9CYJ7"
    }
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()

def authenticate():
    if 'email' in st.session_state and 'password' in st.session_state:
        try:
            st.session_state.person = auth.create_user_with_email_and_password(email, password)
        except:
            try:
                st.session_state.signin = auth.sign_in_with_email_and_password(email, password)
            except:
                st.write("Password invalid!")

def login():
    prepare_authentication()
    st.markdown("##Log in/create account:")
    email = st.input("Email", key = 'email')
    password = st.input("Password", key = 'password')
    authenticate()
    
#Main code begins here
st.title("FUELICIENT")
login()