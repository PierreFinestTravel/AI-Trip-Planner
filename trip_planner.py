import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Load master cheat sheet
@st.cache_data
def load_cheat_sheet():
    file_path = "cheat_sheet_full.xlsx"
    df = pd.read_excel(file_path)
    return df

cheat_sheet = load_cheat_sheet()

# Extract categories
hotels = cheat_sheet[cheat_sheet['Type'] == 'Accommodation']['Name'].unique()
golf_courses = cheat_sheet[cheat_sheet['Type'] == 'Golf']['Name'].unique()
activities = cheat_sheet[cheat_sheet['Type'] == 'Activity']['Name'].unique()
transport_options = cheat_sheet[cheat_sheet['Type'] == 'Transport']['Name'].unique()

st.title("Trip Builder – Streamlit Version")
st.markdown("Plan the full itinerary, auto-fill nights and dates, and download Excel output.")

trip_data = []

num_days = st.number_input("How many trip days?", min_value=1, max_value=60, value=10)
start_date = st.date_input("Trip Start Date", value=date.today())

hotel_memory = ""
room_memory = ""
meal_memory = ""
last_hotel_day = -1
stay_nights = 0

for i in range(num_days):
    st.subheader(f"Day {i+1}")
    with st.container():
        day_date = start_date + timedelta(days=i)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Date:** {day_date.strftime('%Y-%m-%d')}")
        with col2:
            region = st.text_input("Region / Subregion", key=f"region_{i}")
        with col3:
            place = st.text_input("City / Town / Reserve", key=f"place_{i}")

        if i > last_hotel_day:
            hotel = st.selectbox("Hotel", options=[""] + sorted(hotels.tolist()), key=f"hotel_{i}")
            room_type = st.text_input("Room Type", key=f"room_{i}")
            meal_plan = st.text_input("Meal Plan", key=f"meal_{i}")
            stay_nights = st.number_input("# of Nights at Hotel", min_value=1, max_value=num_days - i, value=1, key=f"stay_{i}")
            hotel_memory = hotel
            room_memory = room_type
            meal_memory = meal_plan
            last_hotel_day = i + stay_nights - 1
        else:
            hotel = hotel_memory
            room_type = room_memory
            meal_plan = meal_memory

        golf = st.multiselect("Golf", options=sorted(golf_courses.tolist()), key=f"golf_{i}")
        acts = st.multiselect("Activities", options=sorted(activities.tolist()), key=f"acts_{i}")
        transport = st.multiselect("Transport", options=sorted(transport_options.tolist()), key=f"trans_{i}")
        notes = st.text_area("Notes", key=f"notes_{i}")

    trip_data.append({
        "Trip Day": i + 1,
        "Date": day_date.strftime('%Y-%m-%d'),
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
