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
        user = auth.create_user_with_email_and_password(email, password)
        st.session_state['signin'] = user
        st.session_state.email = user['email']
        return True
    except:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['signin'] = user
            st.session_state.email = user['email']
            return True
        except:
            st.session_state.pop('signin', None)
            st.session_state.pop('email', None)
            st.write("Password invalid!")
            return False

def login():
    auth = prepare_authentication()
    st.markdown("## Log in/create account:")
    email = st.text_input("Email", key = "email")
    password = st.text_input("Password", type="password", key = "password") # try "example"
    if st.button("Create account/log in"):
        if "signin" not in st.session_state:
            if authenticate(auth, email, password):
                st.experimental_rerun()

def post_login():
    print("Post login")
    st.write(f"Signed in as {st.session_state.signin['email']}") # By this point, the user is guaranteed to be signed in.
    
#Main code begins here
st.title("FUELICIENT")

if "signin" not in st.session_state:
    login()

if "signin" in st.session_state:
    post_login()