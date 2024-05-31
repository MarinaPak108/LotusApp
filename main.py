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
layer = "Controller"
@app.route("/")
def home():
    try: 
        day = Service.getDay()
        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        names = wb.sheetnames
        if (day not in names):
            app.logger.info('%s : day - %s', layer, day)
            return redirect('/assign')
        else:
            ws = wb["current"]
            header = [cell.value for cell in ws[1]]
            records = Service.countPatients(Service, wb, day)
            printErrorInLoggerThrowException(records)
        
            return render_template('start.html', title="Список отчетов", tab = header, records = records)
        #raise Exception("error in getWB:")
    except Exception as e:
            return redirectToErrorPage(str(e), __name__)
       
@app.route('/assign')
def my_form():
    try:
        day = Service.getDay()
        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        isButtonActive=False
        ws = wb['settings']
        doctors = Service.fromExcelToList(Doctor, ws)
        printErrorInLoggerThrowException(doctors)
        if (day not in wb.sheetnames):
            isButtonActive = True
        return render_template('assign.html', doctors = doctors, isActive = isButtonActive)
    except Exception as e:
            return redirectToErrorPage(str(e), __name__)
        
@app.route('/assign', methods=['POST'])
def my_form_post():
    try:
        docId = request.form['text']
        day = Service.getDay()

        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        ws_new = wb.create_sheet(day) 
        ws_header = ["Время","ФИО пациента", "М\Ж\Р", "Дата рождения", "Причина", "Давление"]
        ws_new.append(ws_header)
        app.logger.info('%s : added worksheet (%s)', layer, day)
        
        wsDoc = wb["settings"]
        docName = wsDoc[docId][1].value
        
        new_data = [day, docName, -1, docId]
        ws = wb["current"]
        ws.append(new_data)
        wb.save("records/medical.xlsx")
        app.logger.info('%s : saved doctor (%s) name - %s', layer, docId, docName)
        app.logger.info('%s : saved document with new data', layer)
        return redirect("/")
    except Exception as e:
        return  redirectToErrorPage(str(e), __name__)
        
@app.route('/day/<id>', defaults={'errid': 0, 'name': None})
@app.route('/day/<id>/<errid>/<name>')
def patients(id, errid, name):
    try:
        error = ""
        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        isActiveDay = False
        if(id == Service.getDay):
            isActiveDay = True
        if(errid=="1"):
            error = "ФИО "+name+" с идентичной датой рождения уже существует. Пожалуйста проверьте еще раз данные."
        if(id in wb.sheetnames):
            ws = wb[id]  
            patients= Service.fromExcelToList(Patient, ws)
            printErrorInLoggerThrowException(patients)
            return render_template('patient.html', 
                                    patients = patients, 
                                    day = id, 
                                    isActive = isActiveDay, 
                                    length = len(patients)+1, 
                                    error = error)
        else:
            return redirect("/")
    except Exception as e:
            return  redirectToErrorPage(str(e), __name__)
        
@app.route('/day/<id>', methods=['POST'])
def patients_post(id):
    try:
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
        printErrorInLoggerThrowException(url)
        return redirect(url)
    except Exception as e:
           return  redirectToErrorPage(str(e), __name__)

@app.route('/day/<id>/<errid>/<name>', defaults={'errid': 0, 'name': None},  methods=['POST'])
def patients_post_error(id):
    try:
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
        printErrorInLoggerThrowException(url)
        return redirect(url)
    except Exception as e:
            redirectToErrorPage(str(e), __name__)

#################################################################################
#to print error msg from service layer and then redirect via Exception to error.html page
def printErrorInLoggerThrowException(variableToCheck):
    if((type(variableToCheck) is str) and variableToCheck.startswith("error")):
                app.logger.error('Service msg: %s', variableToCheck)
                raise Exception
#to save to logger msg and redirect to error page
def redirectToErrorPage(msg, name):
    app.logger.error('%s : in def %s - %s', layer,name, msg)
    return render_template('error.html')
################################################################################### 
if __name__ == "__main__":
    import logging   
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    FlaskUI(app=app, server="flask",  width= 800, height=600).run()
  