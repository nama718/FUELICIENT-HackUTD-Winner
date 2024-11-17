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
      'measurementId': "G-BTKNF9CYJ7",
      "databaseURL": "https://fuelicient.firebaseapp.com/"
    }
    firebase = pyrebase.initialize_app(firebaseConfig)
    return firebase.auth()

def authenticate(auth, email, password):
    print(f"Beginning authentication with email = {email} and password = {password}")
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.session_state['signin'] = user
        st.session_state.email = user['email']
        print("User created")
        return True
    except Exception as e1:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['signin'] = user
            st.session_state.email = user['email']
            print("User logged in")
            print(e1)
            return True
        except Exception as e2:
            st.session_state.pop('signin', None)
            st.session_state.pop('email', None)
            print("Login failed")
            print(e2)
            st.write("Password invalid!")
            return False

def login():
    print("About to log in")
    auth = prepare_authentication()
    st.markdown("## Log in/create account:")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password") # try "example"
    if st.button("Create account/log in"):
        if "signin" not in st.session_state:
            print("About to authenticate")
            if authenticate(auth, email, password):
                print("About to rerun")
                st.rerun()

def post_login():
    print("Post login")
    st.write(f"Signed in as {st.session_state.signin['email']}") # By this point, the user is guaranteed to be signed in.
    
#Main code begins here
st.title("FUELICIENT")

if "signin" not in st.session_state:
    login()

if "signin" in st.session_state:
    post_login()