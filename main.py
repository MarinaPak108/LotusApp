import os
from flaskwebgui import FlaskUI
from datetime import date, datetime
from flask import Flask, redirect, request, render_template

from models.doctor import Doctor
from models.patient import Patient
from models.record import Record
from service.service import Service

app = Flask(__name__)

directory = os.getcwd()

@app.route("/")
def home():
    day = Service.getDay()
    wb = Service.getWB()
    names = wb.sheetnames
    if (day not in names):
        return redirect('/assign')
    else:
        ws = wb["current"]
        header = [cell.value for cell in ws[1]]
        records = Service.countPatients(Service, wb, day)
        
        return render_template('start.html', title="Список отчетов", tab = header, records = records)

@app.route('/assign')
def my_form():
    day = Service.getDay()
    wb = Service.getWB()
    isButtonActive=False
    ws = wb['settings']
    doctors = Service.fromExcelToList(Doctor, ws)
    if (day not in wb.sheetnames):
        isButtonActive = True
    return render_template('assign.html', doctors = doctors, isActive = isButtonActive)

@app.route('/assign', methods=['POST'])
def my_form_post():
    docId = request.form['text']
    day = Service.getDay()

    wb = Service.getWB()
    
    ws_new = wb.create_sheet(day) 
    ws_header = ["Время","ФИО пациента", "М\Ж\Р", "Дата рождения", "Причина", "Давление"]
    ws_new.append(ws_header)
    
    wsDoc = wb["settings"]
    docName = wsDoc[docId][1].value
    
    new_data = [day, docName, -1, docId]
    ws = wb["current"]
    ws.append(new_data)
    wb.save("records/medical.xlsx")
    return redirect("/")

@app.route('/day/<id>', defaults={'errid': 0, 'name': None})
@app.route('/day/<id>/<errid>/<name>')
def patients(id, errid, name):
    error = ""
    wb = Service.getWB()
    isActiveDay = False
    if(id == str(date.today())):
        isActiveDay = True
    if(errid=="1"):
        error = "ФИО "+name+" с идентичной датой рождения уже существует. Пожалуйста проверьте еще раз данные."
    if(id in wb.sheetnames):
         ws = wb[id]  
         patients= Service.fromExcelToList(Patient, ws)
         return render_template('patient.html', 
                                patients = patients, 
                                day = id, 
                                isActive = isActiveDay, 
                                length = len(patients)+1, 
                                error = error)
    else:
        return redirect("/")
    
@app.route('/day/<id>', methods=['POST'])
def patients_post(id):
    patient_id = request.form['id']
    patient_name = request.form['name']
    patient_type = request.form['type']
    patient_birthdate = request.form['birthdate']
    patient_reason = request.form['reason']
    patient_pressure = request.form['pressure']
    url = Service.checkSavePatientGetPage(Service,
                                          id,
                                          patient_id,
                                          patient_name,
                                          patient_type,
                                          patient_birthdate,
                                          patient_reason,
                                          patient_pressure)
    return redirect(url)

@app.route('/day/<id>/<errid>/<name>', defaults={'errid': 0, 'name': None},  methods=['POST'])
def patients_post_error(id):
    patient_id = request.form['id']
    patient_name = request.form['name']
    patient_type = request.form['type']
    patient_birthdate = request.form['birthdate']
    patient_reason = request.form['reason']
    patient_pressure = request.form['pressure']
    url = Service.checkSavePatientGetPage(Service,
                                          id,
                                          patient_id,
                                          patient_name,
                                          patient_type,
                                          patient_birthdate,
                                          patient_reason,
                                          patient_pressure)
    return redirect(url)




if __name__ == "__main__":
  FlaskUI(app=app, server="flask",  width= 800, height=600).run()
  