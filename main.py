import os
from flaskwebgui import FlaskUI
from flask import Flask, redirect, request, render_template
import logging   

from model.doctor import Doctor
from model.patient import Patient 
from service.service import Service

from error.error import Error_msg

app = Flask(__name__)
layer = "=============> Controller"
day = Service.getDay()

#count calender end date for grown ups and children
grownUp = Service.countGrownUp()
century = Service.countCentury()

##external path to records folder
records_path = os.path.join(os.getcwd(), "records")
folder_path =os.path.join(records_path, day)
medical_file = os.path.join(os.getcwd(), "records/medical.xlsx")
report_file= os.path.join(os.getcwd(), "records/report.xlsx")


@app.route("/")
def home():
    try: 
        wb = Service.getWB(medical_file)
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
            records = Service.countPatients(Service, wb, day, medical_file)
            printErrorInLoggerThrowException(records)
        
            return render_template('start.html', title="Список отчетов", tab = header, records = records)
        #raise Exception("error in getWB:")
    except Exception as e:
            if len(e.args)==1:
                err = Service.fromErrorMsgToEnum(str(e))
            elif len(e.args) == 2 :
                err = Service.fromErroToEnum(e.errno)    
            if(err in Error_msg.__members__):
                msg = Error_msg[err].value
                return redirectToErrorPage(str(e), "def "+request.endpoint, msg)
            else:
                return redirectToErrorPage(str(e), "def "+request.endpoint)
       
@app.route('/assign')
def my_form():
    try:
        wb = Service.getWB(medical_file)
        printErrorInLoggerThrowException(wb)
        #create new work sheet with today date, add header
        ws_new = wb.create_sheet(day) 
        ws_header = ["ID", "Время","ФИО пациента", "Врач", "Врач_Индекс", "М\Ж\Р", "Дата рождения", "Причина", "Давление"]
        ws_new.append(ws_header)
        app.logger.info('%s def %s : added worksheet (%s)', layer,request.endpoint ,day)
        #save at current work sheet doctor infomation for today
        new_data = [day, -1]
        Service.saveRecord(wb, "current", new_data, medical_file)
        app.logger.info('%s def %s: saved document with new data', layer,request.endpoint)
        
        #create header for doctors:
        wb_report = Service.getWB(report_file)
        ws_report = wb_report.create_sheet(day)
        ws_rHeader = ["ID", "ФИО врача", "Специализация", "Ассистент", "М", "Ж", "Р", "Итого"]
        ws_report.append(ws_rHeader)
        
        #get all doctors
        ws_settings = wb["settings"]
        for i in range(2,ws_settings.max_row+1):
            args =[cell.value for cell in ws_settings[i]]
            ws_report.append(args)
        wb_report.save(report_file)
        return redirect("/")
    except Exception as e:
        return  redirectToErrorPage(str(e), "def "+request.endpoint)
        
@app.route('/day/<id>', defaults={'errid': 0, 'name': None})
@app.route('/day/<id>/<errid>/<name>')
def patients(id, errid, name):
    try:
        msg = ""
        wb = Service.getWB(medical_file)
        msg = request.args.get('msg')
        if(msg == None):
            msg = ""
        printErrorInLoggerThrowException(wb)
        isActiveDay = False
                        
        if(id == day):
            isActiveDay = True
        if(errid=="1"):
            app.logger.info('%s def %s : patient %s already exists', layer, request.endpoint , name)
            msg = "ФИО "+name+" уже существует. Пожалуйста проверьте еще раз данные."
        if(id in wb.sheetnames):
            
            wsd = wb['settings']
            docs = Service.fromExcelToList(Doctor, wsd)
            printErrorInLoggerThrowException(docs)

            ws = wb[id]
            patients= Service.fromExcelToList(Patient, ws)
            printErrorInLoggerThrowException(patients)
            
            doctors, filtered = Service.sortDoctors(docs, patients)
            
            app.logger.info('%s def %s : number of patients in %s equals %s', layer, request.endpoint, id, len(patients))
            return render_template('patient.html', 
                                    patients = patients, 
                                    day = id, 
                                    doctors = doctors,
                                    isActive = isActiveDay, 
                                    length = len(patients), 
                                    grown = grownUp,
                                    century = century,
                                    fDoc = filtered,
                                    error = msg)
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
        patient_pressure = "n/a"
        patient_docId = request.form['doc']
        patient_doc = Service.getDocName(Service, patient_docId, medical_file)
        url = Service.checkSavePatientGetPage(Service,
                                            id,
                                            patient_id,
                                            patient_name,
                                            patient_type,
                                            patient_birthdate,
                                            patient_reason,
                                            patient_pressure,
                                            patient_doc,
                                            patient_docId,
                                            medical_file,
                                            folder_path)
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
        patient_pressure = "n/a"
        patient_docId = request.form['doc']
        patient_doc = Service.getDocName(Service, patient_docId, medical_file)
        url = Service.checkSavePatientGetPage(Service,
                                            id,
                                            patient_id,
                                            patient_name,
                                            patient_type,
                                            patient_birthdate,
                                            patient_reason,
                                            patient_pressure,
                                            patient_doc,
                                            patient_docId,
                                            medical_file,
                                            folder_path)
        printErrorInLoggerThrowException(url)
        app.logger.info('%s def %s : patient %s_%s saved to excel', layer, request.endpoint , patient_id, patient_name)
        return redirect(url)
    except Exception as e:
            redirectToErrorPage(str(e), "def "+request.endpoint)

@app.route('/count/<id>')
def count(id):
    try:
        reports = Service.countDoctors(Service, day, id, medical_file, report_file)
        return  render_template("summary.html", reports = reports, day = id)
    except Exception as e:
            redirectToErrorPage(str(e), "def "+request.endpoint)

@app.route('/docListPrint/<docId>', methods = ['GET'])
def doctor_list_print_patients (docId):
    try:
        msg = Service.getDoctorList(Service, medical_file, folder_path, day, docId)
        return redirect("/day/%s?msg=%s"%(day,msg))
    except Exception as e:
            redirectToErrorPage(str(e), "def "+request.endpoint)
    
#################################################################################
#settings for doctors list update/hide/create:
@app.route("/doctors")
def doctors_list():
    try:
        wb=Service.getWB(medical_file)
        printErrorInLoggerThrowException(wb)
        ws = wb["settings"]
        docs = Service.fromExcelToList(Doctor, ws)
        return render_template("doctors.html", doctors=docs, isActive = False)
    except Exception as e:
        return redirectToErrorPage(str(e), "def "+request.endpoint)   

@app.route('/doctors', methods =["POST"])    
def doctors_list_post():
    try:
        doc_id = request.form['id']  
        dname = request.form['dname'] 
        spec = request.form['spec'] 
        nurse = request.form['nurse'] 
        isActive = request.form['active'] 
        Service.saveDoctor(Service, medical_file, report_file, doc_id, dname, spec, nurse, isActive)
        return redirect('/doctors')        
    except Exception as e:
        err = Service.fromErroToEnum(e.errno)
        err_msg = Service.fromErrorMsgToEnum(e.strerror)
        if(err in Error_msg.__members__ or err_msg in Error_msg.__members__):
            msg = Error_msg[err].value
            return redirectToErrorPage(str(e), "def "+request.endpoint, msg)
        else:
            return redirectToErrorPage(str(e), "def "+request.endpoint)
            
#################################################################################
#to print error msg from service layer and then rais Exception
def printErrorInLoggerThrowException(variableToCheck):
    if((type(variableToCheck) is str) and variableToCheck.startswith("error")):
                app.logger.error('Service msg: %s', variableToCheck)
                raise Exception (variableToCheck)
#to save to logger msg and redirect to error.html page
def redirectToErrorPage(msg, name, user_msg=''):
    app.logger.error('%s : in def %s - %s', layer,name, msg)
    return render_template('error.html', msg = user_msg)
################################################################################### 
if __name__ == "__main__":
    
    #create folder for today
    if(os.path.isdir(folder_path)==False):
        os.makedirs(folder_path)
    #save logs file to today folder
    logfile = os.path.join(folder_path, 'debug.log')
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    FlaskUI(app=app, server="flask").run()
  