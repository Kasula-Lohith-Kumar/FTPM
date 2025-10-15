import streamlit as st
from security import registration as reg
from security import authentication as aut
from pages import home
from google_sheets import gsheets_operations as gso
from google_sheets import gsheets_config as gsc

# Hides the default sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .block-container {
            padding-left: 6rem;
            padding-right: 2rem;
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

def run():
    # --- How to display this on your Home Page ---
    # You can use tabs or expanders to separate Registration and Login

    # In your main Streamlit file (e.g., streamlit_app.py):

    print('In Login 🔐 Page')
    st.header("Welcome to the Finance App")
    st.write("Please register or log in to access your portfolio dashboard.")

    # Create two tabs: Login and Register
    tab1, tab2 = st.tabs(["🔒 Login", "✍️ Register"])

    # with tab2:
    #     r.registration_form()

    with tab2:
        print('✍️ Register tab')
    # Call the registration form and check its return value
        registration_status = reg.registration_form()
    
        if registration_status:
            print('✅ Registration Sucessful')
            # If registration was successful, hide the form 
            # and display a message pointing to the Login tab (tab1).
        
            # The form is hidden because registration_form() returns True and 
            # the st.success() message is displayed within the function call.
        
            # You can add a clear instruction here:
            st.markdown("---")
            st.info("✅ **Ready to go!** Please click on the **Login** tab to continue.")

    with tab1:
        print('🔒 Login tab')
        st.subheader("Login")
        # Add your login form fields here (Username, Password)
        # The login logic would involve reading the Google Sheet to check the credentials.
        username_login = st.text_input("Username")
        password_login = st.text_input("Password", type="password")

        if st.button("Login"):
            print('Login button press ☑️')
            if aut.login_verification(username_login, password_login):
                print(f'Welcome to Finance App : {username_login}!')
                st.info("✅ Login successful!")
                st.session_state['page_status'] = 'welcome'
                print(f"Page Status : {st.session_state['page_status']}")
                st.session_state['username'] = username_login
                return st.session_state['page_status'] 
            else:
                st.error("❌ Login failed: Incorrect UserName/Password.")
    
    st.markdown("""
        <style>
            .floating-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9999;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create container for the button
    button_container = st.container()
    with button_container:
        print('Button Container')
        st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Back to Main Page", key="float_back"):
            print('⬅️ Back to Main Page button press ☑️')
            st.session_state['page_status'] = 'home'
            print(f"Page Status : {st.session_state['page_status']}")
            st.switch_page("finance_app_main.py")
        st.markdown('</div>', unsafe_allow_html=True)

if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'home'
    print('Page status updated to home')
    print('Switching ➡️  🏠️ Page')
    st.switch_page('pages/home.py')

if st.session_state['page_status'] == 'login':
    print('Page Status : login')
    st.session_state['key_file_data'] = aut.load_key_file_data()
    sheet = gso.connect_to_worksheet(gsc.SPREADSHEET_ID,  st.session_state['key_file_data'])
    if sheet:
        st.session_state['work_sheet'] = sheet
        print('Connected to Sheet ✅')
        st.session_state['topic_cache_data'] = sheet.acell('K2').value
        if st.session_state['topic_cache_data'] is None:
            st.session_state['topic_cache_data'] = {}
    else:
        print("❌ Could not proceed with registration due to a connection error.")

    status = run() 
    print(f"page state : {st.session_state['page_status']}")
    if status == 'welcome':
        print('Switching ➡️  Welcome 👋 Page')
        st.switch_page('pages/welcome.py')