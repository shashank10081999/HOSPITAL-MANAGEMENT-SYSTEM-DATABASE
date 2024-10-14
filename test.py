from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Database Connection
db_connection = mysql.connector.connect(host="localhost", user="root", password="Shashank@007", database="hospital")

def run_query(query, params=None):
    with db_connection.cursor(buffered=True) as cursor:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
    return result


@app.route('/')
def dashboard():
    patient_count = get_count("Patient")
    doctor_count = get_count("Doctor")
    room_count = get_count("Room")
    room_status = get_room_status()
    return render_template('dashboard.html', patient_count=patient_count, doctor_count=doctor_count, room_count=room_count, room_status=room_status)

def get_count(table_name):
    query = f"SELECT COUNT(*) FROM {table_name}"
    return run_query(query)[0][0]

def get_room_status():
    query = "SELECT type, status, COUNT(*) FROM Room GROUP BY type, status"
    return pd.DataFrame(run_query(query), columns=['Type', 'Status', 'Count'])


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        contact_info = request.form['contact_info']
        gender = request.form['gender']

        query = """
                INSERT INTO Patient (name, dob, address, contact_info, gender)
                VALUES (%s, %s, %s, %s, %s)
                """
        with db_connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (name, dob, address, contact_info, gender))
        return redirect(url_for('dashboard'))
    return render_template('add_patient.html')


@app.route('/search_patients', methods=['GET', 'POST'])
def search_patients():
    if request.method == 'POST':
        search_term = request.form['search_term']
        patients = search_patients_query(search_term)
        return render_template('search_results.html', patients=patients)
    return render_template('search_patients.html')

def search_patients_query(search_term):
    query = "SELECT * FROM Patient WHERE name LIKE %s"
    return pd.DataFrame(run_query(query, (f"%{search_term}%",)), columns=['ID', 'Name', 'DOB', 'Address', 'Contact Info', 'Gender', 'Medical Record Id', 'Insurance Id'])

@app.route('/schedule_appointment', methods=['GET', 'POST'])
def schedule_appointment():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        purpose = request.form['purpose']

        query = """
                INSERT INTO Appointment (patient_id, doctor_id, date, time, purpose)
                VALUES (%s, %s, %s, %s, %s)
                """
        with db_connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (patient_id, doctor_id, date, time, purpose))

        return redirect(url_for('schedule_appointment')) # Redirect after form submission

    # Fetch and display upcoming appointments
    query = "SELECT * FROM Appointment"
    with db_connection.cursor(buffered=True) as cursor:
        cursor.execute(query)
        appointments = cursor.fetchall()

    return render_template('schedule_appointment.html', appointments=appointments)

def get_doctors():
    query = "SELECT * FROM Doctor"
    doctors_df = pd.DataFrame(run_query(query), columns=['ID', 'Name', 'Specialization', 'Contact Info', 'Department ID'])
    doctors = doctors_df.to_dict(orient='records')
    print(doctors)
    return doctors

@app.route('/doctor_management', methods=['GET', 'POST'])
def doctor_management():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        contact_info = request.form['contact_info']
        department_id = request.form['department_id']

        query = """
                INSERT INTO Doctor (name, specialization, contact_info, department_id)
                VALUES (%s, %s, %s, %s)
                """
        run_query(query, (name, specialization, contact_info, department_id))
        return redirect(url_for('doctor_management'))

    doctors = get_doctors()
    return render_template('doctor_management.html', doctors=doctors)

@app.route('/staff_management', methods=['GET', 'POST'])
def staff_management():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department_id = request.form['department_id']

        query = """
                INSERT INTO Staff (name, position, department_id)
                VALUES (%s, %s, %s)
                """
        run_query(query, (name, position, department_id))
        return redirect(url_for('staff_management'))

    staff = get_staff()
    return render_template('staff_management.html', staff=staff)

def get_staff():
    query = "SELECT * FROM Staff"

    staff_df = pd.DataFrame(run_query(query), columns=['ID', 'Name', 'Position', 'Department ID'])
    staff = staff_df.to_dict(orient='records')
    return staff

@app.route('/room_equipment_management', methods=['GET', 'POST'])
def room_equipment_management():
    if request.method == 'POST':
        if 'update_room' in request.form:
            room_id = request.form['room_id']
            room_status = request.form['room_status']
            update_room_status(room_id, room_status)

        if 'update_equipment' in request.form:
            equipment_id = request.form['equipment_id']
            equipment_status = request.form['equipment_status']
            update_equipment_status(equipment_id, equipment_status)

    room_df, equipment_df = get_room_equipment_management()
    return render_template('room_equipment_management.html', rooms=room_df, equipment=equipment_df)

def get_room_equipment_management():
    room_query = "SELECT * FROM Room"
    room_df = pd.DataFrame(run_query(room_query), columns=['ID', 'Type', 'Status', 'Department ID'])
    room = room_df.to_dict(orient='records')

    equipment_query = "SELECT * FROM Equipment"
    equipment_df = pd.DataFrame(run_query(equipment_query), columns=['ID', 'Name', 'Status', 'Department ID'])
    equipment = equipment_df.to_dict(orient='records')

    return room, equipment

def update_room_status(room_id, status):
    query = """
            UPDATE Room SET status = %s WHERE ID = %s
            """
    run_query(query, (status, room_id))

def update_equipment_status(equipment_id, status):
    query = """
            UPDATE Equipment SET status = %s WHERE ID = %s
            """
    run_query(query, (status, equipment_id))

@app.route('/patient_care_management', methods=['GET', 'POST'])
def patient_care_management():
    care_details = None
    care = None

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')

        query = """
                SELECT mr.patient_id, mr.diagnosis, mr.treatment, mr.date, m.name, m.manufacturer,
                p.dosage, p.instructions, n.name AS nurse_name, n.contact_info AS nurse_contact_info,
                s.type, t.name, t.result
                FROM Medical_record mr
                INNER JOIN Medication m ON m.patient_id = mr.patient_id
                INNER JOIN Prescription p ON m.medication_id = p.medication_id
                INNER JOIN Nurse n ON p.nurse_id = n.nurse_id
                INNER JOIN Surgery s ON m.patient_id = s.patient_id
                INNER JOIN Test t ON m.patient_id = t.patient_id
                WHERE mr.patient_id = %s
                """
        care_details = pd.DataFrame(run_query(query, (patient_id,)), 
                                    columns=['patient_id', 'diagnosis', 'treatment', 'date', 
                                             'medication_name', 'manufacturer', 'dosage', 'instructions', 
                                             'nurse_name', 'nurse_contact_info', 'surgery_type', 
                                             'test_name', 'test_result'])
        
        care = care_details.to_dict(orient='records')

    return render_template('patient_care_management.html', care_details=care)

@app.route('/billing_details', methods=['GET', 'POST'])
def billing_details():
    billing_info = None
    billing = None

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')

        query = """
                SELECT i.patient_id, i.provider, i.policy_number, b.amount, b.date, b.payment_method
                FROM Insurance i
                INNER JOIN Billing b ON i.patient_id = b.patient_id
                WHERE i.patient_id = %s
                """
        billing_info = pd.DataFrame(run_query(query, (patient_id,)), 
                                    columns=["patient_id", "provider", "policy_number", 
                                             "amount", "date", "payment_method"])
        
        billing = billing_info.to_dict(orient='records')

    return render_template('billing_details.html', billing_info=billing)



if __name__ == '__main__':
    app.run(debug=True)
