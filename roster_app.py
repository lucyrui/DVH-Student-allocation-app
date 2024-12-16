import streamlit as st
import pandas as pd
import datetime
import io

# --- APP TITLE ---
st.title("DVH Theatre Student Placement Allocation")
st.subheader("Automatically generate placement allocation forms")

# --- INPUT SECTION ---
# Sidebar inputs for student and placement details
st.sidebar.header("Student Details")
student_name = st.sidebar.text_input("Student Name", "")
year_group = st.sidebar.text_input("Year Group", "")
student_no = st.sidebar.text_input("Student Number", "")
email_address = st.sidebar.text_input("Email Address", "")

st.sidebar.header("Roster Configuration")
num_weeks = st.sidebar.number_input("Number of Weeks", min_value=1, max_value=10, value=4)
start_date = st.sidebar.date_input("Start Date", datetime.date.today())

# Assessor and Supervisor Names
educator_name = st.sidebar.text_input("Practice Educator/Assessor Name", "Paul Puttee")
supervisor_1 = st.sidebar.text_input("Practice Supervisor 1", "Lili Starvar")
supervisor_2 = st.sidebar.text_input("Practice Supervisor 2", "")
supervisor_3 = st.sidebar.text_input("Practice Supervisor 3", "")

# Roster Pattern (Sick leave, LD, etc.)
roles = ["E - 8-6", "LD - 8-7", "SL - Sick Leave", ""]  # Dropdown options
colors = {"E - 8-6": "#FFDDC1", "LD - 8-7": "#FFABAB", "SL - Sick Leave": "#FFC3A0", "": "#FFFFFF", "MATCH": "#90EE90"}  # Added green for match

# Table generator based on weeks and days
def generate_roster(start_date, num_weeks):
    days = ["M", "T", "W", "T", "F", "S", "S"]
    dates = []
    current_date = start_date
    
    for week in range(num_weeks):
        for day in days:
            dates.append((f"Week {week+1}", day, current_date.strftime("%d/%m/%Y")))
            current_date += datetime.timedelta(days=1)
            
    return pd.DataFrame(dates, columns=["Week", "Day", "Date"])

roster_df = generate_roster(start_date, num_weeks)

# --- USER INPUT FOR ROSTER ---
st.write("### Input Placement Allocation Details")
roster_table = []
for index, row in roster_df.iterrows():
    role_student = st.selectbox(f"Student Role for {row['Date']} ({row['Week']} {row['Day']})", roles, key=f"student_{index}")
    role_supervisor = st.selectbox(f"Supervisor Role for {row['Date']} ({row['Week']} {row['Day']})", roles, key=f"supervisor_{index}")
    match_color = "MATCH" if role_student == role_supervisor and role_student != "" else role_student
    roster_table.append([row["Week"], row["Day"], row["Date"], role_student, role_supervisor, match_color])

# Final table with inputs
final_roster = pd.DataFrame(roster_table, columns=["Week", "Day", "Date", "Student Role", "Supervisor Role", "Match Color"])

# --- DISPLAY ROSTER WITH COLOR CODING ---
st.write("### Generated Placement Roster")
def color_cells(val):
    color = colors.get(val, "#FFFFFF")
    return f'background-color: {color}; color: black;'

styled_roster = final_roster.style.applymap(color_cells, subset=["Student Role", "Supervisor Role", "Match Color"])
st.dataframe(styled_roster)

# --- STUDENT DETAILS ---
st.write("### Student Details")
st.write(f"**Name:** {student_name}")
st.write(f"**Year Group:** {year_group}")
st.write(f"**Student Number:** {student_no}")
st.write(f"**Email:** {email_address}")
st.write(f"**Practice Educator/Assessor:** {educator_name}")
st.write(f"**Practice Supervisors:** {supervisor_1}, {supervisor_2}, {supervisor_3}")

# --- EXPORT TO EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Placement Roster", index=False)
        workbook = writer.book
        worksheet = writer.sheets['Placement Roster']

        # Apply color coding
        for row_num, row in enumerate(df.itertuples(), start=2):
            for col_num, value in enumerate([row._4, row._5, row._6], start=4):
                color = colors.get(value, "#FFFFFF")
                cell_format = workbook.add_format({'bg_color': color})
                worksheet.write(row_num-1, col_num-1, value, cell_format)

    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(final_roster)

st.download_button(
    label="Download Roster as Excel",
    data=excel_data,
    file_name="student_placement_roster.xlsx",
    mime="application/vnd.ms-excel"
)
