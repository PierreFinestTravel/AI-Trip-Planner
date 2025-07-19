import streamlit as st
import pandas as pd
from datetime import date

# Load master cheat sheet
@st.cache_data
def load_cheat_sheet():
    file_path = "cheat_sheet.xlsx"
    df = pd.read_excel(file_path)
    return df

cheat_sheet = load_cheat_sheet()

# Extract categories
hotels = cheat_sheet[cheat_sheet['Type'] == 'Accommodation']['Name'].unique()
golf_courses = cheat_sheet[cheat_sheet['Type'] == 'Golf']['Name'].unique()
activities = cheat_sheet[cheat_sheet['Type'] == 'Activity']['Name'].unique()
transport_options = cheat_sheet[cheat_sheet['Type'] == 'Transport']['Name'].unique()

# Password protection
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password_input = st.text_input("Enter password", type="password")
    if password_input == st.secrets["password"]["trip_password"]:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

st.title("Trip Builder – Streamlit Version")
st.markdown("Enter each day's trip details and download the full plan as Excel.")

trip_data = []

num_days = st.number_input("How many trip days?", min_value=1, max_value=60, value=10)

for i in range(num_days):
    st.subheader(f"Day {i+1}")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            trip_date = st.date_input(f"Date (Day {i+1})", value=date.today(), key=f"date_{i}")
        with col2:
            region = st.text_input("Region / Subregion", key=f"region_{i}")
        with col3:
            place = st.text_input("City / Town / Reserve", key=f"place_{i}")

        hotel = st.selectbox("Hotel", options=[""] + sorted(hotels.tolist()), key=f"hotel_{i}")
        room_type = st.text_input("Room Type", key=f"room_{i}")
        meal_plan = st.text_input("Meal Plan", key=f"meal_{i}")

        golf = st.multiselect("Golf", options=sorted(golf_courses.tolist()), key=f"golf_{i}")
        acts = st.multiselect("Activities", options=sorted(activities.tolist()), key=f"acts_{i}")
        transport = st.multiselect("Transport", options=sorted(transport_options.tolist()), key=f"trans_{i}")

        notes = st.text_area("Notes", key=f"notes_{i}")

    trip_data.append({
        "Trip Day": i + 1,
        "Date": trip_date,
        "Region / Subregion": region,
        "City / Town / Reserve": place,
        "Hotel": hotel,
        "Room Type": room_type,
        "Meal Plan": meal_plan,
        "Golf": ", ".join(golf),
        "Activities": ", ".join(acts),
        "Transport": ", ".join(transport),
        "Notes": notes
    })

if st.button("Download Trip Plan as Excel"):
    df = pd.DataFrame(trip_data)
    df.to_excel("Trip_Plan_Output.xlsx", index=False)
    with open("Trip_Plan_Output.xlsx", "rb") as f:
        st.download_button("Download Excel File", f, file_name="Trip_Plan.xlsx")
