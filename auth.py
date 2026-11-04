import streamlit as st
import sqlite3

def init_db():
    conn = sqlite3.connect('ev_users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            identifier TEXT NOT NULL
        )
    ''')
    # Default test account
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)', ('admin', 'password123', 'Admin User', 'admin@ev.com'))
    conn.commit()
    conn.close()

def init_auth_state():
    init_db()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "auth_step" not in st.session_state:
        st.session_state.auth_step = "enter_identifier"
    if "temp_identifier" not in st.session_state:
        st.session_state.temp_identifier = ""

def logout():
    st.session_state.logged_in = False
    st.session_state.auth_step = "enter_identifier"
    st.session_state.username = ""
    st.session_state.name = ""
    st.rerun()

def check_login():
    init_auth_state()
    
    # Apply Blue / Black / White Theme & Sidebar Hiding Rule
    if not st.session_state.get("logged_in", False):
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none; }
                .stApp { background-color: #0b0f19; color: #ffffff; }
                .stTextInput input { background-color: #121826; color: #ffffff; border: 1px solid #1e90ff; }
                .stButton button { background-color: #1e90ff; color: white; font-weight: bold; border-radius: 6px; }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><h1 style='text-align: center; color: #00ffcc;'>⚡ EV Range Intelligence Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #a0aec0;'>Secure Academic Evaluation & Telemetry System</p><br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # STEP 1: Enter Email or Phone Number
            if st.session_state.auth_step == "enter_identifier":
                st.markdown("### Step 1: Account Access")
                identifier = st.text_input("Enter your Email or Phone Number", key="input_identifier")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Continue", use_container_width=True, key="btn_continue"):
                        if identifier.strip():
                            st.session_state.temp_identifier = identifier.strip()
                            
                            # Check database for existing identifier
                            conn = sqlite3.connect('ev_users.db')
                            c = conn.cursor()
                            c.execute('SELECT * FROM users WHERE identifier = ?', (identifier.strip(),))
                            exists = c.fetchone()
                            conn.close()
                            
                            if exists:
                                st.session_state.auth_step = "login"
                                st.rerun()
                            else:
                                st.session_state.auth_step = "create_profile"
                                st.rerun()
                        else:
                            st.warning("Please enter a valid email or phone number.")
                with col_b:
                    if st.button("Existing User? Login", use_container_width=True, key="btn_goto_login"):
                        st.session_state.auth_step = "login"
                        st.rerun()

            # STEP 2: Create Name & Password (For New Users)
            elif st.session_state.auth_step == "create_profile":
                st.markdown("### Step 2: Complete Your Profile")
                st.info(f"Registering with: **{st.session_state.temp_identifier}**")
                
                new_username = st.text_input("Choose a Username", key="new_user_input")
                new_name = st.text_input("Your Full Name", key="new_name_input")
                new_password = st.text_input("Create Password", type="password", key="new_pwd_input")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pwd_input")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Create Account", use_container_width=True, key="btn_create_acc"):
                        if not new_username or not new_name or not new_password:
                            st.error("Please fill in all fields.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            try:
                                conn = sqlite3.connect('ev_users.db')
                                c = conn.cursor()
                                c.execute('INSERT INTO users VALUES (?, ?, ?, ?)', 
                                          (new_username, new_password, new_name, st.session_state.temp_identifier))
                                conn.commit()
                                conn.close()
                                st.success("Account created successfully in database! Please login.")
                                st.session_state.auth_step = "login"
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Username already exists in database. Choose another.")
                with col_b:
                    if st.button("Back", use_container_width=True, key="btn_back_step1"):
                        st.session_state.auth_step = "enter_identifier"
                        st.rerun()

            # STEP 3: Login with Created Username & Password
            elif st.session_state.auth_step == "login":
                st.markdown("### Step 3: Login with Credentials")
                
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Login", use_container_width=True, key="btn_final_login"):
                        conn = sqlite3.connect('ev_users.db')
                        c = conn.cursor()
                        c.execute('SELECT password, name FROM users WHERE username = ?', (username,))
                        row = c.fetchone()
                        conn.close()
                        
                        if row and row[0] == password:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.name = row[1]
                            st.success(f"Welcome back, {row[1]}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                with col_b:
                    if st.button("Start Over", use_container_width=True, key="btn_restart"):
                        st.session_state.auth_step = "enter_identifier"
                        st.rerun()
        return False

    # If logged in, apply blue theme styling for dashboard
    st.markdown("""
        <style>
            .stApp { background-color: #0b0f19; color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)
    return True