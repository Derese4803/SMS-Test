import streamlit as st
import pandas as pd

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(page_title="Nursery Data Correction", layout="wide")

# ─── SESSION STATE INIT ──────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "logged_in_as" not in st.session_state:
    st.session_state.logged_in_as = None
if "user" not in st.session_state:
    st.session_state.user = None
if "master_log" not in st.session_state:
    st.session_state.master_log = []

# ─── DUMMY DATA (Replace with your actual data loading) ───
@st.cache_data
def load_data():
    # Replace these with your actual data sources
    df_c = pd.DataFrame({
        'number': [101, 102],
        'constraint': ['Age > 0', 'Yield <= Area'],
        'value': [-5, 500],
        'respondent_name': ['Abebe', 'Kebede'],
        'phone_no': ['0911', '0922'],
        'kebele_name': ['Gulele', 'Kirkos'],
        'username': ['enum1', 'enum2']
    })
    df_l = pd.DataFrame({
        'number': [103],
        'constraint': ['Date invalid'],
        'value': ['2025-13-45'],
        'farmer_name': ['Chala'],
        'phone_number': ['0933'],
        'kebele': ['Bole'],
        'username': ['enum1']
    })
    return df_c, df_l

df_c, df_l = load_data()

# Combine consistency and logic errors
combined = pd.concat([df_c, df_l], ignore_index=True)

# Fixed records from master_log
if st.session_state.master_log:
    fixed_df = pd.DataFrame(st.session_state.master_log)
else:
    fixed_df = pd.DataFrame(columns=['user', 'number', 'type', 'reason', 'fix'])

# Records not yet fixed
fixed_numbers = set(fixed_df['number'].values) if not fixed_df.empty else set()
remaining_df = combined[~combined['number'].isin(fixed_numbers)].copy()

# ─── STYLED METRIC BOX ───────────────────────────────────
def styled_metric(label, value, color):
    st.markdown(
        f"""
        <div style="
            background-color: {color}20;
            border-left: 5px solid {color};
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        ">
            <p style="margin: 0; color: #666; font-size: 14px;">{label}</p>
            <p style="margin: 0; color: {color}; font-size: 28px; font-weight: bold;">{value}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─── LOGIN SCREEN ────────────────────────────────────────
def login_screen():
    st.title("🔐 Nursery Data Correction System")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Enumerator Login")
        enum_user = st.text_input("Username", key="enum_user")
        enum_pass = st.text_input("Password", type="password", key="enum_pass")
        if st.button("Login as Enumerator"):
            # Replace with real auth
            if enum_user and enum_pass:
                st.session_state.logged_in = True
                st.session_state.logged_in_as = "enumerator"
                st.session_state.user = enum_user
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with col2:
        st.subheader("Admin Login")
        admin_user = st.text_input("Username", key="admin_user")
        admin_pass = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Login as Admin"):
            # Replace with real auth
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.logged_in_as = "admin"
                st.session_state.user = admin_user
                st.rerun()
            else:
                st.error("Invalid admin credentials")

# ─── LOGOUT ──────────────────────────────────────────────
def logout():
    if st.sidebar.button("🚪 Logout"):
        for key in ['logged_in', 'logged_in_as', 'user']:
            st.session_state[key] = None if key != 'logged_in' else False
        st.rerun()
[7/20/2026 12:09 PM] @ Dere: # ─── ENUMERATOR VIEW ─────────────────────────────────────
def enumerator_view():
    st.subheader(f"📝 Error Correction - {st.session_state.user}")
    st.write(f"Remaining errors: {len(remaining_df)}")
    
    if remaining_df.empty:
        st.success("🎉 All errors have been corrected!")
        return
    
    for idx, row in remaining_df.iterrows():
        record_id = row.get('number', f"unknown_{idx}")
        error_label = "Consistency Error" if record_id in df_c['number'].values else "Logic Error"
        
        with st.expander(f"{error_label} (ID: {record_id})"):
            st.markdown("### 👤 Respondent Profile")
            name_to_show = row.get('respondent_name') or row.get('farmer_name') or "N/A"
            phone_to_show = row.get('phone_no') or row.get('phone_number') or "N/A"
            kebele_to_show = row.get('kebele_name') or row.get('kebele') or "N/A"
            
            c1, c2 = st.columns(2)
            c1.write(f"Name: {name_to_show}")
            c1.write(f"Phone: {phone_to_show}")
            c2.write(f"Kebele: {kebele_to_show}")
            
            st.markdown("---")
            st.markdown("### 🔍 Error Details")
            st.info(f"Rule: {row.get('constraint', 'N/A')}")
            st.warning(f"Current Value: {row.get('value', 'N/A')}")
            
            # Use record_id for stable widget keys
            reason = st.text_area("Reason for error", key=f"reason_{record_id}")
            fix = st.text_input("Corrected Value", key=f"fix_{record_id}")
            
            if st.button("Submit Fix", key=f"submit_{record_id}"):
                if not reason.strip() or not fix.strip():
                    st.error("⚠️ Please provide both a reason and corrected value.")
                else:
                    st.session_state.master_log.append({
                        'user': st.session_state.user,
                        'number': record_id,
                        'type': error_label,
                        'reason': reason,
                        'fix': fix,
                        'timestamp': pd.Timestamp.now().isoformat()
                    })
                    st.success("✅ Fix recorded successfully!")
                    st.rerun()

# ─── ADMIN VIEW ──────────────────────────────────────────
def admin_view():
    st.subheader("📊 Admin Correction Dashboard")
    
    # Calculations (renamed 'remaining' to 'remaining_count' to avoid shadowing)
    total_errors = len(combined)
    total_corrected = len(fixed_df)
    total_consistency = len(df_c)
    total_logic = len(df_l)
    remaining_count = total_errors - total_corrected
    
    # Custom Color-Coded Boxes
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: styled_metric("Total", total_errors, "#6c757d")      # Gray
    with c2: styled_metric("Corrected", total_corrected, "#28a745")  # Green
    with c3: styled_metric("Consistency", total_consistency, "#007bff")  # Blue
    with c4: styled_metric("Logic", total_logic, "#fd7e14")       # Orange
    with c5: styled_metric("Remaining", remaining_count, "#dc3545")   # Red
    
    st.markdown("---")
    
    # Enumerator Stats
    st.write("### 👥 Performance by Enumerator")
    
    if 'username' in combined.columns:
        stats = combined.groupby('username')['number'].count().reset_index()
        stats.columns = ['Enumerator', 'Assigned']
    else:
        stats = pd.DataFrame(columns=['Enumerator', 'Assigned'])
    
    if not fixed_df.empty and 'user' in fixed_df.columns:
        f_stats = fixed_df.groupby('user')['number'].count().reset_index()
        f_stats.columns = ['Enumerator', 'Fixed']
    else:
        f_stats = pd.DataFrame(columns=['Enumerator', 'Fixed'])
    
    final = pd.merge(stats, f_stats, on='Enumerator', how='left').fillna(0)
[7/20/2026 12:09 PM] @ Dere: final['Fixed'] = final['Fixed'].astype(int)
    final['Remaining'] = final['Assigned'] - final['Fixed']
    st.dataframe(final, use_container_width=True)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Data", "✅ Corrected", "📈 Performance", "📊 Statistics"])
    
    with tab1:
        st.dataframe(combined, use_container_width=True)
    
    with tab2:
        st.dataframe(fixed_df, use_container_width=True)
        if not fixed_df.empty:
            csv = fixed_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Corrected Data",
                csv,
                "corrected_data.csv",
                "text/csv"
            )
    
    with tab3:
        if not fixed_df.empty and 'user' in fixed_df.columns:
            st.bar_chart(fixed_df['user'].value_counts())
        else:
            st.info("No corrections made yet.")
    
    with tab4:
        status_df = pd.DataFrame({
            "Status": ["Fixed", "Remaining"],
            "Count": [len(fixed_df), remaining_count]
        }).set_index("Status")
        st.bar_chart(status_df)

# ─── MAIN ────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_screen()
    else:
        logout()
        st.sidebar.write(f"Logged in as: {st.session_state.user}")
        st.sidebar.write(f"Role: {st.session_state.logged_in_as.title()}")
        
        if st.session_state.logged_in_as == "enumerator":
            enumerator_view()
        elif st.session_state.logged_in_as == "admin":
            admin_view()
        else:
            st.error("Unknown role. Please log in again.")
            st.session_state.logged_in = False
            st.rerun()

if name == "main":
    main()
