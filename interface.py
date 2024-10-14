import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# Database connection setup (replace with your database credentials)
db_connection = mysql.connector.connect(host="localhost",user="root",password="Shashank@007",database="hospital")

# Function to run queries
def run_query(query):
    with db_connection.cursor(buffered=True) as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return result

# Sidebar for navigation
with open("master.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Hospital Management System")
option = st.selectbox(
    'Choose an option',
    ('Dashboard', 'Patient Management', 'Appointment Scheduling', 
     'Doctor Management', 'Staff Management', 'Room and Equipment Management' , "Patient Care Management" , "Billing Details")
)

def run_query(query):
    with db_connection.cursor(buffered=True) as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return result

# Function to get counts
def get_count(table_name):
    query = f"SELECT COUNT(*) FROM {table_name}"
    return run_query(query)[0][0]

# Function to get room status
def get_room_status():
    query = "SELECT type, status, COUNT(*) FROM Room GROUP BY type, status"
    return pd.DataFrame(run_query(query), columns=['Type', 'Status', 'Count'])

def show_dashboard():

    # Displaying key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", get_count("Patient"))
    with col2:
        st.metric("Total Doctors", get_count("Doctor"))
    with col3:
        st.metric("Total Rooms", get_count("Room"))

    # Displaying Room Status
    st.subheader("Room Status Overview")
    df_room_status = get_room_status()
    st.dataframe(df_room_status)



# Function to add a new patient
def add_patient(name, dob, address, contact_info, gender):
    with db_connection.cursor(buffered=True) as cursor:
        
        query = f"""
        INSERT INTO Patient (name, dob, address, contact_info, gender)
        VALUES ('{name}','{dob}', '{address}', '{contact_info}', '{gender}')
        """
        cursor.execute(query)

# Function to search for patients
def search_patients(search_term):
    query = f"SELECT * FROM Patient WHERE name LIKE %s"
    return pd.DataFrame(run_query(query, (f"%{search_term}%",)), columns=['ID', 'Name', 'DOB', 'Address', 'Contact Info', 'Gender' , 'Medical Record Id' ,'Insurance Id'])

# Patient Management
def show_patient_management():

    # Form to add a new patient
    with st.form("Add Patient"):
        st.subheader("Register New Patient")
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth")
        address = st.text_area("Address")
        contact_info = st.text_input("Contact Info")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        submit_button = st.form_submit_button("Register Patient")

        if submit_button:
            add_patient(name, dob, address, contact_info, gender)
            st.success("Patient Registered Successfully!")

    # Search for patients
    st.subheader("Search Patients")
    search_term = st.text_input("Enter search term:")
    if search_term:
        search_results = search_patients(search_term)
        st.dataframe(search_results)



def show_appointment_scheduling():

    # Form to schedule a new appointment
    with st.form("Schedule Appointment"):
        st.subheader("Schedule New Appointment")
        patient_id = st.number_input("Patient ID", step=1)
        doctor_id = st.number_input("Doctor ID", step=1)
        date = st.date_input("Date", min_value=datetime.today())
        time = st.time_input("Time")
        purpose = st.text_area("Purpose")
        submit_button = st.form_submit_button("Schedule Appointment")

        if submit_button:
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                INSERT INTO Appointment (patient_id, doctor_id, date, time, purpose)
                VALUES ({patient_id},{doctor_id}, '{date}', '{time}', '{purpose}')
                """
                cursor.execute(query)
            st.success("Appointment Scheduled Successfully!")

    # Display upcoming appointments
    st.subheader("Upcoming Appointments")
    query = "SELECT * FROM Appointment"

    if run_query(query) is None:
        st.write("There are no upcoming appointments")

    appointments_df =  pd.DataFrame(run_query(query), columns=['ID', 'Patient ID', 'Doctor ID', 'Date', 'Time', 'Purpose'])
    appointments_df['Time'] = appointments_df['Time'].astype(str)
    st.dataframe(appointments_df)


def get_doctors():
    query = "SELECT * FROM Doctor"
    return pd.DataFrame(run_query(query), columns=['ID', 'Name', 'Specialization', 'Contact Info', 'Department ID'])

# Doctor Management
def show_doctor_management():
    # Form to add a new doctor
    with st.form("Add Doctor"):
        st.subheader("Add New Doctor")
        name = st.text_input("Name")
        specialization = st.text_input("Specialization")
        contact_info = st.text_input("Contact Info")
        department_id = st.number_input("Department ID", step=1)
        submit_button = st.form_submit_button("Add Doctor")

        if submit_button:
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                INSERT INTO Doctor (name, specialization, contact_info, department_id)
                VALUES ('{name}','{specialization}', {contact_info}, {department_id})
                """
                cursor.execute(query)
            st.success("Doctor Added Successfully!")

    # Display doctors
    st.subheader("Doctors")
    doctors_df = get_doctors()
    st.dataframe(doctors_df)


def get_staff():
    query = "SELECT * FROM Staff"
    return pd.DataFrame(run_query(query), columns=['ID','Name', 'Position','Department ID'])


def show_staff_management():

    # Form to add a new staff member
    with st.form("Add Staff"):
        st.subheader("Add New Staff Member")
        name = st.text_input("Name")
        position = st.text_input("Position")
        department_id = st.number_input("Department ID", step=1)
        submit_button = st.form_submit_button("Add Staff")

        if submit_button:
            # Function to add staff goes here
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                INSERT INTO Staff (name, position,department_id)
                VALUES ('{name}','{position}', {department_id})
                """
                cursor.execute(query)

            st.success("Staff Member Added Successfully!")

    # Display staff
    st.subheader("Staff Members")
    staff_df = get_staff()
    st.dataframe(staff_df)


def get_room_equipment_management():
    query = "SELECT * FROM Room"
    room_df =  pd.DataFrame(run_query(query), columns=['ID','Type', 'Status','Department ID'])

    query = "SELECT * FROM Equipment"
    equipment_df = pd.DataFrame(run_query(query), columns=['ID','Name', 'Status','Department ID'])

    return room_df , equipment_df

def show_room_equipment_management():

    # Form to manage rooms
    with st.form("Manage Room"):
        st.subheader("Manage Room")
        room_id = st.number_input("Room ID", step=1)
        room_status = st.selectbox("Status", ["Available", "Occupied", "Maintenance"])
        room_submit_button = st.form_submit_button("Update Room")

        if room_submit_button:
             with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                UPDATE Room SET status =  '{room_status}'
                where room_id = {room_id}
                """
                cursor.execute(query)

             st.success("Room Status Updated Successfully!")

    # Form to manage equipment
    with st.form("Manage Equipment"):
        st.subheader("Manage Equipment")
        equipment_id = st.number_input("Equipment ID", step=1)
        equipment_status = st.selectbox("Equipment Status", ["Good", "Maintenance", "Repair"])
        equipment_submit_button = st.form_submit_button("Update Equipment")

        if equipment_submit_button:
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                UPDATE Equipment SET status =  '{equipment_status}'
                where equipment_id = {equipment_id}
                """
                cursor.execute(query)
            st.success("Equipment Status Updated Successfully!")

    

    room_df , equipment_df = get_room_equipment_management()


    # Display current room and equipment status
    st.subheader("Current Room Status")
    st.dataframe(room_df)

    st.subheader("Current Equipment Status")
    st.dataframe(equipment_df)

def show_patient_care_management():
    with st.form("Patient ID"):
        st.subheader("Patient ID")
        patient_id = st.number_input("Patient ID", step=1)

        button = st.form_submit_button("Care Deatils")

        if button:
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                select mr.patient_id , mr.diagnosis ,mr.treatment , mr.date , m.name , m.manufacturer , p.dosage , p.instructions , n.name as "Nurse name"  , n.contact_info as " Nurse Contact Info" , s.type , t.name , t.result
                from Medical_record mr 
                inner join Medication m on m.patient_id = mr.patient_id
                inner join Prescription p on m.medication_id = p.medication_id
                inner join Nurse n on p.nurse_id = n.nurse_id
                inner join Surgery s on m.patient_id = s.patient_id
                inner join Test t on m.patient_id = t.patient_id
                where mr.patient_id = {patient_id}
                """
                cursor.execute(query)

                df = pd.DataFrame(run_query(query), columns=['patient_id','diagnosis', 'treatment','date' , 'medication_name' , 'manufacturer' , "dosage" , "instructions" , "nurse_name" , "nurse_contact_info" , "surgery_type" , "test_name" , "test_result"])

            st.dataframe(df)


def show_billing_details():
    with st.form("Patient ID"):
        st.subheader("Patient ID")
        patient_id = st.number_input("Patient ID", step=1)

        button = st.form_submit_button("Care Deatils")

        if button:
            with db_connection.cursor(buffered=True) as cursor:
        
                query = f"""
                select i.patient_id , i.provider , i.policy_number , b.amount, b.date, b.payment_method from Insurance i 
                inner join Billing b on i.patient_id = b.patient_id
                where i.patient_id = {patient_id}
                """
                cursor.execute(query)

                df = pd.DataFrame(run_query(query), columns=["patient_id" , "provider" , "policy_number" , "amount", "date", "payment_method"])

            st.dataframe(df)


            

    



# Dashboard
if option == 'Dashboard':
    st.title("Hospital Dashboard")
    show_dashboard()

# Patient Management
elif option == 'Patient Management':
    st.title("Patient Management")
    show_patient_management()

# Appointment Scheduling
elif option == 'Appointment Scheduling':
    st.title("Appointment Scheduling")
    show_appointment_scheduling()

# Doctor Management
elif option == 'Doctor Management':
    st.title("Doctor Management")
    show_doctor_management()

# Staff Management
elif option == 'Staff Management':
    st.title("Staff Management")
    show_staff_management()

# Room and Equipment Management
elif option == 'Room and Equipment Management':
    st.title("Room and Equipment Management")
    show_room_equipment_management()

elif option == "Patient Care Management":
    st.title("Patient Care Management")
    show_patient_care_management()

elif option == 'Billing Details':
    st.title("Billing Details")
    show_billing_details()
    
