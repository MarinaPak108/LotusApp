import os
from flaskwebgui import FlaskUI
from flask import Flask, redirect, request, render_template
import logging   

from model.doctor import Doctor
from model.patient import Patient 
from service.service import Service

app = Flask(__name__)
layer = "=============> Controller"
day = Service.getDay()

#count calender end date for grown ups and children
grownUp = Service.countGrownUp()
century = Service.countCentury()

##external path to records folder
records_path = os.path.join("C:", "records")
folder_path =os.path.join(records_path, day)
medical_file = os.path.join(records_path, "medical.xlsx")

@app.route("/")
def home():
    try: 
        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        names = wb.sheetnames
        if (day not in names):
            app.logger.info('%s def %s: day - %s', layer, request.endpoint,  day)
            yesterday_path = os.path.join(records_path, names[-1])
            if(os.path.isdir(yesterday_path)):
                yesterday_path = os.path.join(yesterday_path, "medical.xlsx")
                wb.save(yesterday_path) 
            return redirect('/assign')
        else:
            ws = wb["current"]
            header = [cell.value for cell in ws[1]]
            records = Service.countPatients(Service, wb, day)
            printErrorInLoggerThrowException(records)
        
            return render_template('start.html', title="Список отчетов", tab = header, records = records)
        #raise Exception("error in getWB:")
    except Exception as e:
            return redirectToErrorPage(str(e), "def "+request.endpoint)
       
@app.route('/assign')
def my_form():
    try:
        wb = Service.getWB()
        printErrorInLoggerThrowException(wb)
        isButtonActive=False
        ws = wb['settings']
        doctors = Service.fromExcelToList(Doctor, ws)
        printErrorInLoggerThrowException(doctors)
        app.logger.info('%s def %s : number of doctors in %s equals %s', layer, request.endpoint, day, len(doctors))
        if (day not in wb.sheetnames):
            isButtonActive = True
        return render_template('assign.html', doctors = doctors, isActive = isButtonActive)
    except Exception as e:
            return redirectToErrorPage(str(e), "def "+request.endpoint)
        
@app.route('/assign', methods=['POST'])
def my_form_post():
    try:
        wb = Service.getWB()
        docId = request.form['text']
        printErrorInLoggerThrowException(wb)
        ws_new = wb.create_sheet(day) 
        ws_header = ["ID", "Время","ФИО пациента", "М\Ж\Р", "Дата рождения", "Причина", "Давление"]
        ws_new.append(ws_header)
        app.logger.info('%s def %s : added worksheet (%s)', layer,request.endpoint ,day)
        
        wsDoc = wb["settings"]
        docName = wsDoc[docId][1].value
        
        new_data = [day, docName, -1, docId]
        Service.saveRecord(wb, "current", new_data, medical_file)
        #ws = wb["current"]
        #ws.append(new_data)
        #wb.save(medical_file)
        app.logger.info('%s def %s : saved doctor (%s) name - %s on day %s', layer,request.endpoint, docId, docName, day)
        app.logger.info('%s def %s: saved document with new data', layer,request.endpoint)
        return redirect("/")
    except Exception as e:
        return  redirectToErrorPage(str(e), "def "+request.endpoint)
        
@app.route('/day/<id>', defaults={'errid': 0, 'name': None})
@app.route('/day/<id>/<errid>/<name>')
def patients(id, errid, name):
    try:
        wb = Service.getWB()
        error = ""
        printErrorInLoggerThrowException(wb)
        isActiveDay = False
        if(id == day):
            isActiveDay = True
        if(errid=="1"):
            app.logger.info('%s def %s : patient %s already exists', layer, request.endpoint , name)
            error = "ФИО "+name+" с идентичной датой рождения уже существует. Пожалуйста проверьте еще раз данные."
        if(id in wb.sheetnames):
            ws = wb[id]  
            patients= Service.fromExcelToList(Patient, ws)
            printErrorInLoggerThrowException(patients)
            app.logger.info('%s def %s : number of patients in %s equals %s', layer, request.endpoint, id, len(patients))
            return render_template('patient.html', 
                                    patients = patients, 
                                    day = id, 
                                    isActive = isActiveDay, 
                                    length = len(patients)+1, 
                                    grown = grownUp,
                                    century = century,
                                    error = error)
        else:
            return redirect("/")
    except Exception as e:
            return  redirectToErrorPage(str(e), "def "+request.endpoint)
        
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
        app.logger.info('%s def %s : patient %s_%s saved to excel', layer, request.endpoint , patient_id, patient_name)
        return redirect(url)
    except Exception as e:
           return  redirectToErrorPage(str(e), "def "+request.endpoint)

@app.route('/day/<id>/<errid>/<name>', defaults={'errid': 0, 'name': None},  methods=['POST'])
def patients_post_error(id, errid, name):
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
        app.logger.info('%s def %s : patient %s_%s saved to excel', layer, request.endpoint , patient_id, patient_name)
        return redirect(url)
    except Exception as e:
            redirectToErrorPage(str(e), "def "+request.endpoint)

#################################################################################
#to print error msg from service layer and then rais Exception
def printErrorInLoggerThrowException(variableToCheck):
    if((type(variableToCheck) is str) and variableToCheck.startswith("error")):
                app.logger.error('Service msg: %s', variableToCheck)
                raise Exception
#to save to logger msg and redirect to error.html page
def redirectToErrorPage(msg, name):
    app.logger.error('%s : in def %s - %s', layer,name, msg)
    return render_template('error.html')
################################################################################### 
if __name__ == "__main__":
    
    #create folder for today
    if(os.path.isdir(folder_path)==False):
        os.makedirs(folder_path)
    #save logs file to today folder
    logfile = os.path.join(folder_path, 'debug.log')
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    FlaskUI(app=app, server="flask",  width= 800, height=600).run()
  