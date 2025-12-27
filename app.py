import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import utils

# --- Configuration ---
st.set_page_config(
    page_title="Automotive Project Development Tracker",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar by default
)

# --- Automatic Backup on Startup ---
@st.cache_resource
def run_backup_on_startup():
    utils.backup_database()
    return True

run_backup_on_startup()

# Custom CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: #ffffff; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
    h1, h2, h3 { color: #111827; } /* Dark text for headers */
    
    /* Scrollbar styling */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #888; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }
    
    /* Ensure Chart backgrounds match if needed, largely handled by theme */

</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
projects = utils.load_data()


# --- App Header (Centered with Logo) ---
h_col1, h_col2, h_col3 = st.columns([1, 6, 1])
with h_col1:
    st.image("logo.png", width=100) # Logo at top left

with h_col2:
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Automotive Project Development Tracker</h1>", unsafe_allow_html=True)



# --- Session State for Navigation ---
if 'view' not in st.session_state:
    st.session_state.view = "Dashboard"

def set_view(view_name):
    st.session_state.view = view_name

# --- Top Navigation Tiles ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 60px;
div.stButton > button:first-child {
    width: 100%;
    height: 3em; 
    font-weight: bold;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns(3)

with nav_c1:
    if st.button("📊 Dashboard", type="primary" if st.session_state.view == "Dashboard" else "secondary"):
        set_view("Dashboard")
        st.rerun()

with nav_c2:
    if st.button("🏗️ Detailed Project View", type="primary" if st.session_state.view == "Detailed Project View" else "secondary"):
        set_view("Detailed Project View")
        st.rerun()

with nav_c3:
    if st.button("📅 Gantt View", type="primary" if st.session_state.view == "Gantt View" else "secondary"):
        set_view("Gantt View")
        st.rerun()


st.divider()

# --- Sidebar Disabled (User Request) ---
# Filters moved to main dashboard area
# Sidebar block removed effectively by not creating st.sidebar elements if not needed.
# Or we can keep it for "Advanced Settings" later, but for now user requested removal.


# --- Default Selection for First Load ---
all_types = sorted(list(set([p.get('type', 'Unknown') for p in projects])))
if 'selected_types' not in st.session_state:
    st.session_state.selected_types = all_types

# --- Filtering Logic (Placeholder, will be updated in Dashboard view) ---
# We initialize filtered_projects here but it will depend on the widget in Dashboard
# To make it accessible globally we might need to render the filter first or use session state.
# For now, we will render the filter inside the Dashboard view and update the list there.
# But other views need it too. So we should probably render the filter at the top OF THE DASHBOARD view only?
# Or TOP of ALL views? User said "Remove filters from left pane and add it to right side above the bar chart".
# This implies it's specific to the dashboard layout.
# However, "Release Matrix" also used 'filtered_projects'.
# We should probably put the filter in a common area if it affects all, BUT user instructions were specific to Dashboard placement.
# Let's assume Filter applies globally but is CONTROLED from the Dashboard (or we duplicate it/move it to top).
# For simplicity and compliance: I will put the filter control IN THE DASHBOARD VIEW as requested.
# For other views, I will either default to ALL or show a small filter expander.
# ACTUALLY, sticking to instructions: "add it to ... above the bar chart".
# So I will define filtered_projects based on session state, and update session state in Dashboard.

filtered_projects = [p for p in projects if p.get('type') in st.session_state.selected_types]

# --- Main Content ---

if st.session_state.view == "Dashboard":
    st.title("Dashboard Overview")
    st.caption("Real-time status of all active programs")

    # Custom styling for Cards
    st.markdown("""
    <style>
        .dash-card {
            background-color: #262730; /* Dark card background */
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
            height: 140px;
            border: 1px solid #3f3f46;
        }
        .dash-card::before {
            content: "";
            position: absolute;
            top: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            opacity: 0.1; /* Lower opacity for dark mode */
        }
        .card-blue::before { background-color: #60a5fa; }
        .card-green::before { background-color: #34d399; }
        .card-yellow::before { background-color: #fbbf24; }
        .card-red::before { background-color: #f87171; }
        
        .card-label { font-size: 0.8rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; display: flex; align-items: center; gap: 5px; color: #e5e7eb; }
        .card-value { font-size: 2.5rem; font-weight: 800; color: #f9fafb; line-height: 1; }
        .card-sub { font-size: 0.8rem; color: #9ca3af; margin-top: 5px; }
        
        /* Status Badge CSS (Modern Pastel) */
        .status-badge {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700; /* Bold */
            display: inline-block;
            margin-bottom: 2px;
            border: 1px solid transparent; /* No border needed for pastel usually */
        }
        /* Pastel Colors */
        .bg-green { background-color: #E6F4EA; color: #137333; } /* On Track */
        .bg-yellow { background-color: #FEF7E0; color: #B06000; } /* At Risk - Darker Orange text for contrast */
        .bg-red { background-color: #FCE8E6; color: #C5221F; } /* Critical */
        .bg-grey { background-color: #F3F4F6; color: #4B5563; } /* Pending */
        
        .plan-date { font-size: 0.7rem; color: #6b7280; margin-top: 2px; display: block; }
        
        /* Table Border Styling for Gateway Status */
        .gateway-table-cell {
            border: 1px solid #f3f4f6; /* Very subtle border */
            padding: 8px;
            text-align: center;
            background-color: #ffffff; 
            color: #1f2937;
            border-radius: 4px; /* Soft edges */
        }
        .gateway-table-header {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
            font-weight: bold;
            color: #111827; 
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Calculate Stats
    stats = utils.calculate_dashboard_stats(filtered_projects)
    # Calculate Adherence Rate (On Time Gateways / Total Completed Gateways)
    total_completed_gws = 0
    on_time_gws = 0
    
    for p in projects: # Use ALL projects for global KPI, or filtered? Usually global. Let's use filtered to match context.
        if p in filtered_projects:
            if 'modules' in p:
                for m in p['modules']:
                    for gw in ['D0','D1','D2','D3','D4']:
                        p_date = p['gateways'].get(gw, {}).get('p')
                        a_date = m['gateways'].get(gw, {}).get('a')
                        if p_date and a_date:
                            total_completed_gws += 1
                            if a_date <= p_date:
                                on_time_gws += 1
    
    adherence_rate = (on_time_gws / total_completed_gws * 100) if total_completed_gws > 0 else 0

    # 1. Overview Cards
    st.markdown("### 🚀 Project Health Overview")
    
    # Adjusted columns for Gauge
    k1, k2, k3, k4, k5 = st.columns([1, 1, 1, 1, 2])
    
    with k1:
        st.markdown(f"""
        <div class="dash-card">
            <div class="card-label">TOTAL PROJECTS</div>
            <div class="card-value">{stats['total']}</div>
            <div class="card-sub">{stats['active']} Active</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k2:
        st.markdown(f"""
        <div class="dash-card card-green">
            <div class="card-label" style="color: #10b981;">● ON TRACK</div>
            <div class="card-value">{stats['green']}</div>
            <div class="card-sub">No Delays</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="dash-card card-yellow">
            <div class="card-label" style="color: #f59e0b;">● AT RISK</div>
            <div class="card-value">{stats['yellow']}</div>
            <div class="card-sub">1-30 Days Delay</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k4:
        st.markdown(f"""
        <div class="dash-card card-red">
            <div class="card-label" style="color: #ef4444;">● CRITICAL</div>
            <div class="card-value">{stats['red']}</div>
            <div class="card-sub">> 30 Days Delay</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = adherence_rate,
            title = {'text': "Module Adherence %", 'font': {'size': 14}}, # Title inside chart
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 50], 'color': "#7f1d1d"}, # Dark Red
                    {'range': [50, 80], 'color': "#78350f"}, # Dark Yellow
                    {'range': [80, 100], 'color': "#064e3b"}], # Dark Green
                'threshold': {
                    'line': {'color': "#fca5a5", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        # Zero margins to fit inside the "tile" height and align with CSS cards
        # Increased height slightly to 160 to fill the space better if needed, or stick to 140
        # CSS cards are 140px. Let's maximize chart usage. 
        # t=30 is needed for title.
        # Updated bgcolor to match dark card, font white for contrast
        fig_gauge.update_layout(height=150, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="#262730", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)


    st.markdown("###")
    
    # Project Gateway Status Matrix
    # Create 2-Column Layout for Detail Section
    d_col1, d_col2 = st.columns([1.5, 1])

    with d_col1:
        st.subheader("Project Gateway Status")
        
        # Header
        cols = st.columns([1.5, 1, 1, 1, 1, 1, 1])
        headers = ["PROJECT", "TYPE", "D0", "D1", "D2", "D3", "D4"]
        for i, h in enumerate(headers):
            cols[i].markdown(f"<div class='gateway-table-header'>{h}</div>", unsafe_allow_html=True)
            
        st.divider()
        
        # Rows
        for p in filtered_projects:
            r_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1])
            r_cols[0].markdown(f"**{p['name']}**")
            r_cols[1].markdown(f"<span style='padding:2px 8px; border-radius:4px; font-size:0.8em; border: 1px solid #3f3f46; color: #9ca3af'>{p['type']}</span>", unsafe_allow_html=True)
            
            gws = ['D0', 'D1', 'D2', 'D3', 'D4']
            for i, gw in enumerate(gws):
                plan = p['gateways'].get(gw, {}).get('p')
                
                # Find Max Actual date for this gateway
                actual_date = p['gateways'].get(gw, {}).get('a') # Use Rolled Up Actual
                status = "grey"
                
                # Use Rolled Up Actual directly for status
                if actual_date:
                    status = utils.get_status(plan, actual_date)
                
                # Render Badge
                def fmt_d(d_str):
                    if not d_str: return "Pending"
                    try: return datetime.strptime(d_str, "%Y-%m-%d").strftime("%b %d")
                    except: return d_str
                
                bg_class = f"bg-{status}"
                badge_text = fmt_d(actual_date) if actual_date else "Pending"
                plan_text = f"Plan: {fmt_d(plan)}" if plan else ""
                
                html = f"""
                <div class="gateway-table-cell">
                    <span class="status-badge {bg_class}">{badge_text}</span>
                    <span class="plan-date">{plan_text}</span>
                </div>
                """
                r_cols[i+2].markdown(html, unsafe_allow_html=True)
                
                
            # Custom Row Separator (Faint Line)
            st.markdown("<div style='border-bottom: 1px solid #f3f4f6; margin-top: 10px; margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    with d_col2:
        # Filters (Moved Here)
        st.caption("Filters")
        
        # Checkbox style filter using multiselect (standard Streamlit closest equivalent to checklist)
        # Or columns of checkboxes. Users usually prefer multiselect for space.
        # But "make it a checkbox filter" might mean literally checkboxes. 
        # I'll use a multiselect as it's cleaner "above the chart".
        
        new_selection = st.multiselect("Project Type", all_types, default=st.session_state.selected_types, key="dash_filter_types")
        if new_selection != st.session_state.selected_types:
            st.session_state.selected_types = new_selection
            st.rerun()

        # Download Report Button
        st.markdown("<br>", unsafe_allow_html=True)
        excel_data = utils.projects_to_excel(filtered_projects)
        file_name_date = datetime.now().strftime("%d-%m-%Y")
        st.download_button(
            label="📥 Download Report (.xlsx)",
            data=excel_data,
            file_name=f"Project_Status_{file_name_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dash_download_xlsx",
            type="primary" # Make it prominent
        )
        
        st.subheader("Module Level Adherence")

        st.caption("Distribution of On-Track, At-Risk, and Critical modules")
        
        # Calculate Adherence (Green, Yellow, Red counts per Project)
        adherence_data = []
        for p in filtered_projects:
            c_green = 0
            c_yellow = 0
            c_red = 0
            
            if 'modules' in p:
                for m in p['modules']:
                    # Check all gateways with actuals
                    for gw in ['D0','D1','D2','D3','D4']:
                        g_data = m['gateways'].get(gw, {})
                        if g_data.get('a'):
                            status = utils.get_status(p['gateways'].get(gw, {}).get('p'), g_data['a'])
                            if status == 'green': c_green += 1
                            elif status == 'yellow': c_yellow += 1
                            elif status == 'red': c_red += 1
            
            adherence_data.append({
                "Project": p['name'], 
                "On Track": c_green, 
                "At Risk": c_yellow, 
                "Critical": c_red
            })
            
        if adherence_data:
            df_adh = pd.DataFrame(adherence_data)
            # Stacked Bar Chart with 3 Colors
            fig_adh = go.Figure(data=[
                go.Bar(name='On Track', x=df_adh['Project'], y=df_adh['On Track'], marker_color='#10b981'),
                go.Bar(name='At Risk', x=df_adh['Project'], y=df_adh['At Risk'], marker_color='#f59e0b'),
                go.Bar(name='Critical', x=df_adh['Project'], y=df_adh['Critical'], marker_color='#f43f5e')
            ])
            fig_adh.update_layout(template="plotly_dark", barmode='stack', height=600, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_adh, use_container_width=True)
        else:
            st.info("No adherence data.")

elif st.session_state.view == "Detailed Project View":
    st.title("Project Details")

        
    # --- Modals (Dialogs) ---
    @st.dialog("➕ Create New Project")
    def modal_create_project():
        with st.form("add_project_form"):
            new_name = st.text_input("Project Name")
            new_type = st.selectbox("Type", ["Major", "Minor", "Carryover"])
            c1, c2 = st.columns(2)
            d0_date = c1.date_input("D0 Start Date")
            num_modules = c2.number_input("Initial Modules", min_value=0, max_value=20, value=1)
            
            submitted = st.form_submit_button("Create Project")
            
            if submitted and new_name:
                new_id = int(datetime.now().timestamp())
                new_proj = {
                    "id": new_id,
                    "name": new_name,
                    "type": new_type,
                    "gateways": { 
                        "D0": { "p": str(d0_date), "a": "" }, 
                        "D1": { "p": "", "a": "" }, 
                        "D2": { "p": "", "a": "" }, 
                        "D3": { "p": "", "a": "" }, 
                        "D4": { "p": "", "a": "" } 
                    },
                    "modules": []
                }
                
                for i in range(num_modules):
                    mod_id = new_id + i + 1
                    project_gw_defaults = { "p": "", "a": "", "ecn": "" }
                    # Set D0 Plan for module same as project start
                    d0_gw = project_gw_defaults.copy()
                    d0_gw['p'] = str(d0_date)
                    
                    new_proj['modules'].append({
                        "id": mod_id,
                        "name": f"Module {i+1}",
                        "gateways": { 
                            "D0": d0_gw, "D1": project_gw_defaults.copy(), 
                            "D2": project_gw_defaults.copy(), "D3": project_gw_defaults.copy(), 
                            "D4": project_gw_defaults.copy() 
                        }
                    })
                
                projects.append(new_proj)
                if utils.save_data(projects):
                    st.success(f"Project '{new_name}' created!")
                    st.rerun()
                else:
                    st.error("Failed to save.")

    @st.dialog("📂 Upload Bulk Data (CSV)")
    def modal_upload_csv():
        st.info("Upload a CSV file to bulk update projects. Data will be merged.")
        
        # Template Download
        template_csv = utils.get_csv_template_data()
        st.download_button(
            label="Download CSV Template",
            data=template_csv,
            file_name="bulk_upload_template.csv",
            mime="text/csv"
        )
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            if st.button("Process Upload"):
                updated_projects, msg = utils.process_csv_upload(uploaded_file, projects)
                if msg == "Success":
                    if utils.save_data(updated_projects):
                        st.success("Data uploaded and merged successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save merged data.")
                else:
                    st.error(msg)
    
    # --- Action Tiles ---
    ac1, ac2 = st.columns(2)
    
    with ac1:
        if st.button("➕ Create New Project", use_container_width=True):
            modal_create_project()
            
    with ac2:
        if st.button("📂 Upload Bulk Data", use_container_width=True):
            modal_upload_csv()


    
    st.divider()

    st.subheader("Gateway Matrix")
    st.caption("Detailed Project & Module Status")

    # Header Row
    h1, h2, h3, h4, h5, h6, h7 = st.columns([2, 1, 1, 1, 1, 1, 1])
    h1.write("**Module Name**")
    h2.write("**Type**")
    h3.markdown("**D0** <br><span style='font-size:0.8em; color:grey'>(Concept)</span>", unsafe_allow_html=True)
    h4.markdown("**D1** <br><span style='font-size:0.8em; color:grey'>(Proto)</span>", unsafe_allow_html=True)
    h5.markdown("**D2** <br><span style='font-size:0.8em; color:grey'>(Pilot)</span>", unsafe_allow_html=True)
    h6.markdown("**D3** <br><span style='font-size:0.8em; color:grey'>(Launch)</span>", unsafe_allow_html=True)
    h7.markdown("**D4** <br><span style='font-size:0.8em; color:grey'>(Close)</span>", unsafe_allow_html=True)
    st.divider()

    # Iterate Projects
    for p in filtered_projects:
        # Filter applied via filtered_projects list
        
        with st.expander(f"**{p['name']}**", expanded=True):
            # Project Plan Data Row
            pc1, pc2, pc3, pc4, pc5, pc6, pc7 = st.columns([2, 1, 1, 1, 1, 1, 1])
            pc2.caption(p.get('type'))

            # Helper to safely parse date or return None
            def parse_date(d_str):
                if not d_str: return None
                try: return datetime.strptime(d_str, "%Y-%m-%d").date()
                except: return None
            
            # Project Gateways Inputs
            with pc3:
                curr_p = p['gateways']['D0'].get('p')
                new_d0 = st.date_input("Plan", value=parse_date(curr_p), key=f"p_{p['id']}_D0", label_visibility="collapsed")
                if str(new_d0) != curr_p and new_d0 is not None:
                     p['gateways']['D0']['p'] = str(new_d0)
                     utils.save_data(projects) # Auto-save (naive)

            with pc4:
                curr_p = p['gateways']['D1'].get('p')
                new_d1 = st.date_input("Plan", value=parse_date(curr_p), key=f"p_{p['id']}_D1", label_visibility="collapsed")
                if str(new_d1) != curr_p and new_d1 is not None:
                     p['gateways']['D1']['p'] = str(new_d1)
                     utils.save_data(projects)

            with pc5:
                curr_p = p['gateways']['D2'].get('p')
                new_d2 = st.date_input("Plan", value=parse_date(curr_p), key=f"p_{p['id']}_D2", label_visibility="collapsed")
                if str(new_d2) != curr_p and new_d2 is not None:
                     p['gateways']['D2']['p'] = str(new_d2)
                     utils.save_data(projects)

            with pc6:
                curr_p = p['gateways']['D3'].get('p')
                new_d3 = st.date_input("Plan", value=parse_date(curr_p), key=f"p_{p['id']}_D3", label_visibility="collapsed")
                if str(new_d3) != curr_p and new_d3 is not None:
                     p['gateways']['D3']['p'] = str(new_d3)
                     utils.save_data(projects)

            with pc7:
                curr_p = p['gateways']['D4'].get('p')
                new_d4 = st.date_input("Plan", value=parse_date(curr_p), key=f"p_{p['id']}_D4", label_visibility="collapsed")
                if str(new_d4) != curr_p and new_d4 is not None:
                     p['gateways']['D4']['p'] = str(new_d4)
                     utils.save_data(projects)
            
            st.markdown("---")

            # Modules
            if 'modules' in p:
                for m_idx, m in enumerate(p['modules']):
                    mc1, mc2, mc3, mc4, mc5, mc6, mc7 = st.columns([2, 1, 1, 1, 1, 1, 1])
                    
                    with mc1:
                        st.write("") # Spacer
                        st.caption("Module")
                        new_name = st.text_input("Name", value=m['name'], key=f"m_name_{m['id']}", label_visibility="collapsed")
                        if new_name != m['name']:
                            m['name'] = new_name
                            utils.save_data(projects)
                    
                    gw_cols = [mc3, mc4, mc5, mc6, mc7]
                    gws = ['D0', 'D1', 'D2', 'D3', 'D4']
                    
                    for i, gw in enumerate(gws):
                        col = gw_cols[i]
                        gw_data = m['gateways'].get(gw, {})
                        
                        gw_status = utils.get_status(p['gateways'].get(gw, {}).get('p'), gw_data.get('a'))
                        
                        # Use markdown for "Card" like feel or Status header
                        # Using emoji is cleanest, or color text
                        status_color_css = {
                            "green": "color: #10b981", 
                            "yellow": "color: #f59e0b", 
                            "red": "color: #f43f5e", 
                            "grey": "color: #94a3b8"
                        }
                        
                        with col:
                            with st.container(border=True):
                                st.markdown(f"<div style='font-size:0.8em; font-weight:bold; {status_color_css[gw_status]}'>{gw} Status</div>", unsafe_allow_html=True)
                                
                                has_subs = bool(m.get('sub_modules'))
                                
                                act_val = parse_date(gw_data.get('a'))
                                st.caption("ACT")
                                new_act = st.date_input("Act", value=act_val, key=f"m_{m['id']}_{gw}_a", label_visibility="collapsed", disabled=has_subs)
                                
                                if has_subs:
                                    # Show info tooltip or just locked icon? 
                                    # Using disabled is enough
                                    pass
                                
                                ecn_val = gw_data.get('ecn', '')
                                st.caption("ECN")
                                new_ecn = st.text_input("ECN", value=ecn_val, placeholder="-", key=f"m_{m['id']}_{gw}_ecn", label_visibility="collapsed")
                                
                                # Update Logic
                                # Allow clearing: if new_act is None, we save empty string
                                if not has_subs:
                                    if new_act != act_val:
                                        clean_new = str(new_act) if new_act else ""
                                        gw_data['a'] = clean_new
                                        utils.save_data(projects)
                                
                                # Note: if has_subs is True, the input is disabled, so user can't change it.
                                # The rollup logic in utils.py will overwrite it anyway on save.
                                        
                                if new_ecn != ecn_val:
                                    gw_data['ecn'] = new_ecn
                                    utils.save_data(projects)
                                    
                            if new_ecn != ecn_val:
                                gw_data['ecn'] = new_ecn
                                utils.save_data(projects)
                                
                    # --- Sub-modules Logic ---
                    sub_mods = m.get('sub_modules', [])
                    for s_idx, s in enumerate(sub_mods):
                        sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([2, 1, 1, 1, 1, 1, 1])
                        with sc1:
                            st.write("") 
                            st.caption("Sub-module")
                            # Visual indentation
                            c_name, c_del = st.columns([4, 1])
                            with c_name:
                                s_name = st.text_input("Name", value=s['name'], key=f"s_name_{s['id']}", label_visibility="collapsed")
                            with c_del:
                                if st.button("🗑️", key=f"del_s_{s['id']}"):
                                    m['sub_modules'].pop(s_idx)
                                    utils.save_data(projects)
                                    st.rerun()

                            st.markdown("<span style='color:grey; font-size:0.8em'>↳ Nested</span>", unsafe_allow_html=True)
                            
                            if s_name != s['name']:
                                s['name'] = s_name
                                utils.save_data(projects)

                        s_gw_cols = [sc3, sc4, sc5, sc6, sc7]
                        for i, gw in enumerate(gws):
                            col = s_gw_cols[i]
                            gw_data = s['gateways'].get(gw, {})
                            
                            # Inherit Project Plan for Status comparison (or should it be independent? Using Project plan for now)
                            gw_status = utils.get_status(p['gateways'].get(gw, {}).get('p'), gw_data.get('a'))
                            
                            with col:
                                with st.container(border=True):
                                    st.markdown(f"<div style='font-size:0.7em; color:grey'>{gw} (Sub)</div>", unsafe_allow_html=True)
                                    
                                    act_val = parse_date(gw_data.get('a'))
                                    new_act = st.date_input("Act", value=act_val, key=f"s_{s['id']}_{gw}_a", label_visibility="collapsed")
                                    
                                    ecn_val = gw_data.get('ecn', '')
                                    new_ecn = st.text_input("ECN", value=ecn_val, placeholder="-", key=f"s_{s['id']}_{gw}_ecn", label_visibility="collapsed")
                                    
                                    # Allow clearing date
                                    if new_act != act_val:
                                        clean_new = str(new_act) if new_act else ""
                                        gw_data['a'] = clean_new
                                        utils.save_data(projects)
                                            
                                    if new_ecn != ecn_val:
                                        gw_data['ecn'] = new_ecn
                                        utils.save_data(projects)
                        st.divider()

                    # Add Sub-module Button
                    if st.button(f"➕ Add Sub-module to {m['name']}", key=f"add_sub_{m['id']}"):
                        if 'sub_modules' not in m:
                            m['sub_modules'] = []
                        
                        defaults = { "p": "", "a": "", "ecn": "" }
                        new_sub_id = int(datetime.now().timestamp() * 1000) + 999 
                        m['sub_modules'].append({
                            "id": new_sub_id,
                            "name": "New Part",
                            "gateways": { "D0": defaults.copy(), "D1": defaults.copy(), "D2": defaults.copy(), "D3": defaults.copy(), "D4": defaults.copy() }
                        })
                        utils.save_data(projects)
                        st.rerun()

                    st.divider() 
            else:
                st.info("No modules added.")
                
            if st.button("➕ Add Module", key=f"add_mod_{p['id']}"):
                defaults = { "p": "", "a": "", "ecn": "" }
                new_mod_id = int(datetime.now().timestamp() * 1000)
                p['modules'].append({
                    "id": new_mod_id,
                    "name": "New Module",
                    "gateways": { "D0": defaults.copy(), "D1": defaults.copy(), "D2": defaults.copy(), "D3": defaults.copy(), "D4": defaults.copy() }
                })
                utils.save_data(projects)
                st.rerun()


elif st.session_state.view == "Gantt View":
    st.title("Project Gantt Chart")
    
    # Gantt Chart Visualization
    # We create a timeline of Projects (Plan) vs Modules (Actuals)
    
    gantt_rows = []
    milestone_data = [] # Store milestones: Task, Date, Label, Color
    task_order = []  # To enforce Y-axis ordering (Project -> Modules -> Next Project)

    for p in filtered_projects:
        # Project Label
        p_label = f"🅿️ {p['name']}"
        task_order.append(p_label)

        # Project Plan Range (D0 to D4)
        if p['gateways'].get('D0', {}).get('p') and p['gateways'].get('D4', {}).get('p'):
             gantt_rows.append({
                "Task": p_label,
                "Start": p['gateways']['D0']['p'],
                "Finish": p['gateways']['D4']['p'],
                "Resource": "Plan",
                "Description": f"Type: {p.get('type')}"
            })
             # Collect Milestones
             for gw in ['D0', 'D1', 'D2', 'D3', 'D4']:
                 d = p['gateways'].get(gw, {}).get('p')
                 if d:
                     milestone_data.append({
                         "Task": p_label, "Date": d, "Gateway": gw, "Type": "Plan", "Color": "#1e3a8a" # darker blue
                     })
             
        # Module Actuals
        if 'modules' in p:
            for m in p['modules']:
                unique_suffix = "\u200B" * p['id'] 
                m_display = f"   └─ {m['name']}{unique_suffix}"
                task_order.append(m_display)
                # Segmented Actuals Logic
                # Use pairs of gateways (Start -> End)
                # D0->D1, D1->D2, D2->D3, D3->D4
                gws_ordered = ['D0', 'D1', 'D2', 'D3', 'D4']
                
                # Get all actual dates for this module
                m_acts = {}
                for gw in gws_ordered:
                    val = m['gateways'].get(gw, {}).get('a')
                    if val: m_acts[gw] = val

                # Iterate pairs
                for i in range(len(gws_ordered) - 1):
                    start_gw = gws_ordered[i]
                    end_gw = gws_ordered[i+1]
                    
                    # We can only draw a segment if both start and end exist?
                    # Or should we draw from last known? 
                    # Prompt: "if D2 is released... D1 to D2 colour..." implies segments between specific gateways.
                    
                    if start_gw in m_acts and end_gw in m_acts:
                        s_date = m_acts[start_gw]
                        e_date = m_acts[end_gw]
                        
                        # Determine status based on the END gateway of the segment
                        # "if D2 is released at risk then D1 to D2 colour should be yellow"
                        
                        # Get Plan for End Gateway
                        end_gw_plan = p['gateways'].get(end_gw, {}).get('p')
                        status = utils.get_status(end_gw_plan, e_date)
                        
                        # Map Status to Resource Label for Coloring
                        status_label = "Actual (On Track)"
                        if status == 'yellow': status_label = "Actual (At Risk)"
                        elif status == 'red': status_label = "Actual (Critical)"
                        
                        gantt_rows.append({
                            "Task": m_display,
                            "Start": s_date,
                            "Finish": e_date,
                            "Resource": status_label,
                            "Description": f"{start_gw} -> {end_gw}: {status.upper()}"
                        })
                     
                # Collect Milestones
                for gw in ['D0', 'D1', 'D2', 'D3', 'D4']:
                    d = m['gateways'].get(gw, {}).get('a')
                    if d:
                        milestone_data.append({
                            "Task": m_display, "Date": d, "Gateway": gw, "Type": "Actual", "Color": "#5b21b6" # darker purple
                        })

    if gantt_rows:
        df_gantt = pd.DataFrame(gantt_rows)
        # 1. Base Timeline (Bars)
        # Custom Colors for Status
        color_map = {
            "Plan": "#3b82f6", # Blue
            "Actual (On Track)": "#10b981", # Green
            "Actual (At Risk)": "#f59e0b", # Yellow
            "Actual (Critical)": "#ef4444" # Red
        }
        
        fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", color="Resource",
                                title="Project Timeline with Milestones",
                                color_discrete_map=color_map,
                                hover_data=["Description"], opacity=0.8, template="plotly_dark")
        
        # Dynamic Height Calculation
        # Base height + (row height * number of tasks)
        # task_order contains all unique Y-axis labels
        chart_height = max(600, len(task_order) * 50 + 100)
        
        fig_gantt.update_layout(
            height=chart_height,
            font=dict(size=14, family="Arial"),
            title_font_size=20,
            xaxis=dict(
                title="Timeline",
                showgrid=True,
                gridwidth=1,
                gridcolor='#666666', # Slightly lighter to handle dots better
                griddash='dot', 
                dtick="M1", # Monthly ticks
                tickformat="%b %Y",
                tickangle=-45
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=14)
            ),
            legend=dict(
                font=dict(size=12)
            )
        )
        
        # 2. Add Milestones (Diamonds)
        if milestone_data:
            df_ms = pd.DataFrame(milestone_data)
            # Add trace for Plan Milestones
            ms_plan = df_ms[df_ms['Type'] == 'Plan']
            if not ms_plan.empty:
                fig_gantt.add_trace(go.Scatter(
                    x=ms_plan['Date'], y=ms_plan['Task'], mode='markers+text',
                    name='Plan Gateway', text=ms_plan['Gateway'],
                    textposition="top center",
                    marker=dict(symbol='diamond', size=12, color='#2563eb', line=dict(color='white', width=1)),
                    hoverinfo='text', hovertext=ms_plan.apply(lambda r: f"{r['Gateway']}: {r['Date']}", axis=1)
                ))
            
            # Add trace for Actual Milestones
            ms_act = df_ms[df_ms['Type'] == 'Actual']
            if not ms_act.empty:
                fig_gantt.add_trace(go.Scatter(
                    x=ms_act['Date'], y=ms_act['Task'], mode='markers+text',
                    name='Actual Gateway', text=ms_act['Gateway'],
                    textposition="bottom center",
                    marker=dict(symbol='diamond', size=12, color='#7c3aed', line=dict(color='white', width=1)),
                    hoverinfo='text', hovertext=ms_act.apply(lambda r: f"{r['Gateway']}: {r['Date']}", axis=1)
                ))

        # Enforce the custom order on Y-axis
        fig_gantt.update_layout(yaxis={'categoryorder':'array', 'categoryarray': task_order})
        fig_gantt.update_yaxes(autorange="reversed") # Layout projects top-down
        
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No timeline data available.")
