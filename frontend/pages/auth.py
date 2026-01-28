"""
Authentication pages - Login and Sign Up
"""
import streamlit as st
import re
from utils.auth import login_user, signup_user, verify_user_email
from utils.ui_helpers import create_alert

def switch_auth_page(page_name):
    """Callback to switch auth page and update sidebar"""
    st.session_state.page = page_name
    st.session_state.auth_radio = page_name

def render_login_page():
    """Render login page"""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
            <div style='padding: 3rem; background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%); 
            border-radius: 12px; color: white; height: 100%;'>
                <h1 style='margin: 0 0 1rem 0;'>Welcome Back!</h1>
                <p style='margin: 0; font-size: 1.1rem; line-height: 1.6;'>
                    Access the MIND News Recommendation System and get personalized news 
                    recommendations powered by advanced similarity search algorithms.
                </p>
                <div style='margin-top: 2rem;'>
                    <p style='font-weight: 600; margin-bottom: 1rem;'>Features:</p>
                    <ul style='margin: 0; padding-left: 1.5rem;'>
                        <li>Personalized news recommendations</li>
                        <li>Track your reading history</li>
                        <li>Explore trending content</li>
                        <li>Advanced analytics</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## Login to Your Account")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Your unique username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Your secure password"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_button = st.form_submit_button("Login", use_container_width=True)
            with col_btn2:
                # We can't use on_click here because it's inside a form
                # But this button just submits the form, we can check it below
                # Actually, submit_button is for the whole form.
                # The "Sign Up" button inside the form is problematic because form widgets can't have callbacks easily/behave differently
                # But wait, looking at the code, there's a st.form_submit_button("Sign Up") inside the form?
                # The user code had:
                # with col_btn2:
                #    st.form_submit_button("Sign Up", use_container_width=True)
                # This button does nothing currently in the original code logic if clicked? 
                # Ah, line 54 in original was `st.form_submit_button("Sign Up"...)`
                # But logic only checked `if submit_button:` (which is the "Login" button).
                # The "Sign Up" usage inside the form is confusing. 
                # The request is about the "Click here to sign up" link/button at the bottom.
                pass
            
            # NOTE: Empty container for layout alignment if needed, or just let the button stay
            # The original code had a Sign Up button inside the login form that did nothing.
            # I will leave the form logic as is to avoid breaking layout, but focus on the bottom button.
            
            with col_btn2:
                 # Use on_click for navigation to avoid session state modification errors
                 st.form_submit_button(
                    "Sign Up", 
                    use_container_width=True,
                    on_click=switch_auth_page, 
                    args=("Sign Up",)
                )
            
            # Removed manual check for signup_form_btn since callback handles it

            if submit_button:
                if not username or not password:
                    create_alert("Please fill in all fields.", "error")
                else:
                    if login_user(username, password):
                        create_alert("Login successful! Redirecting...", "success")
                        st.balloons()
                        st.rerun()
                    else:
                        create_alert("Invalid username or password.", "error")
        
        st.divider()
        
        st.markdown("""
            <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px;'>
                <p style='margin: 0;'>Don't have an account?</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.button(
            "Click here to sign up →", 
            key="signup_nav_btn", 
            use_container_width=True,
            on_click=switch_auth_page,
            args=("Sign Up",)
        )

def render_signup_page():
    """Render signup page"""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
            <div style='padding: 3rem; background: linear-gradient(135deg, #00a8e8 0%, #0066cc 100%); 
            border-radius: 12px; color: white; height: 100%;'>
                <h1 style='margin: 0 0 1rem 0;'>Join MIND Today!</h1>
                <p style='margin: 0; font-size: 1.1rem; line-height: 1.6;'>
                    Create an account and experience the future of personalized news 
                    recommendations powered by machine learning.
                </p>
                <div style='margin-top: 2rem;'>
                    <p style='font-weight: 600; margin-bottom: 1rem;'>Get Started:</p>
                    <ul style='margin: 0; padding-left: 1.5rem;'>
                        <li>Create your account in seconds</li>
                        <li>Verify your email address</li>
                        <li>Start getting recommendations</li>
                        <li>Customize your preferences</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## Create Your Account")
        
        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input(
                "Full Name",
                placeholder="Enter your full name",
                help="Your display name"
            )
            username = st.text_input(
                "Username",
                placeholder="Choose a unique username",
                help="Minimum 3 characters, alphanumeric"
            )
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                help="We'll send a verification code here"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password",
                help="Minimum 8 characters with uppercase and numbers"
            )
            password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password"
            )
            
            terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_button = st.form_submit_button("Create Account", use_container_width=True)
            with col_btn2:
                # Use on_click for navigation
                st.form_submit_button(
                    "Already have an account?", 
                    use_container_width=True,
                    on_click=switch_auth_page,
                    args=("Login",)
                )
            
            # Removed manual check for login_form_btn

            if submit_button:
                # Validation
                errors = []
                
                if not all([full_name, username, email, password, password_confirm]):
                    errors.append("All fields are required.")
                
                if len(username) < 3:
                    errors.append("Username must be at least 3 characters.")
                
                if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                    errors.append("Username can only contain letters, numbers, underscores, and hyphens.")
                
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    errors.append("Please enter a valid email address.")
                
                if len(password) < 8:
                    errors.append("Password must be at least 8 characters.")
                
                if password != password_confirm:
                    errors.append("Passwords do not match.")
                
                if not terms_agreed:
                    errors.append("Please agree to the Terms of Service.")
                
                if errors:
                    for error in errors:
                        create_alert(error, "error")
                else:
                    result = signup_user(username, email, password, full_name)
                    
                    if result['success']:
                        st.session_state.signup_user_id = result['user_id']
                        st.session_state.signup_verification_code = result.get('verification_code', '')
                        st.session_state.page = "Email Verification"
                        create_alert(
                            f"Account created! Verification code: {result.get('verification_code', 'sent to email')}",
                            "success"
                        )
                        st.rerun()
                    else:
                        create_alert(f"{result['message']}", "error")
        
        st.divider()
        
        st.markdown("""
            <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px;'>
                <p style='margin: 0;'>Already have an account?</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.button(
            "Click here to login →", 
            key="login_nav_btn", 
            use_container_width=True, 
            on_click=switch_auth_page,
            args=("Login",)
        )

def render_verification_page():
    """Render email verification page"""
    st.markdown("## Verify Your Email")
    
    if 'signup_user_id' not in st.session_state:
        st.error("Session expired. Please sign up again.")
        st.stop()
    
    create_alert(
        f"Verification code has been sent to your email. Enter it below to complete registration.",
        "info"
    )
    
    with st.form("verification_form"):
        verification_code = st.text_input(
            "Verification Code",
            placeholder="Enter the 6-digit code",
            max_chars=6
        )
        
        submit_button = st.form_submit_button("Verify Email", use_container_width=True)
        
        if submit_button:
            if not verification_code:
                create_alert("Please enter the verification code.", "error")
            else:
                result = verify_user_email(st.session_state.signup_user_id, verification_code)
                
                if result['success']:
                    create_alert("Email verified successfully! You can now log in.", "success")
                    st.balloons()
                    del st.session_state.signup_user_id
                    del st.session_state.signup_verification_code
                    st.session_state.page = "Login"
                    st.rerun()
                else:
                    create_alert(f"{result['message']}", "error")
    
    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.rerun()
