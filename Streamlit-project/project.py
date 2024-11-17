# Thanks to https://stackoverflow.com/a/73293418/23017142
# import sys
# if sys.version_info.major == 3 and sys.version_info.minor >= 10:
#    import collections
#    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

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
    try:
        st.session_state.person = auth.create_user_with_email_and_password(email, password)
    except:
        try:
            st.session_state.signin = auth.sign_in_with_email_and_password(email, password)
        except:
            st.write("Password invalid!")

def login(login_objects): #elsewhere, login_objects is a session_state object. Here, the name is shorter.
    auth = prepare_authentication()
    login_objects.markdown("## Log in/create account:")
    email = login_objects.text_input("Email", key = "email")
    password = login_objects.text_input("Password", type="password", key = "password") # try "example"
    if st.button("Create account/log in"):
        authenticate(auth, email, password)

def post_login(login_objects):
    login_objects.empty() # remove login screen
    st.write(f"Signed in as {st.session_state.signin['email']}") # By this point, the user is guaranteed to be signed in.
    
#Main code begins here
st.title("FUELICIENT")

st.session_state.login_objects = st.empty() # used for creating things which can be deleted later
if not "signin" in st.session_state:
    login(st.session_state.login_objects)

if "signin" in st.session_state:
    post_login(st.session_state.login_objects)