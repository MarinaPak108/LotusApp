from __future__ import print_function
import os
import openpyxl
from datetime import date, datetime
from typing import TypeVar
import pandas as pd
from dateutil.relativedelta import relativedelta

from model.record import Record

from mailmerge import MailMerge
from datetime import date

from model.doctor import Doctor
from model.patient import Patient 

class Service():
    T = TypeVar('T')   
    
    def getWB(path_to_file):
        try:
            return openpyxl.load_workbook(path_to_file)
        except Exception as e:
            return "error in getWB:"+str(e)

    def getDay():
        return str(date.today())

    def getTimestamp():
        return datetime.now()
    
    def fromExcelToList(T, ws):
        try: 
            listObjects=[]
            for i in range(2,ws.max_row+1):
                args =[cell.value for cell in ws[i]]
                typeObject = T(*args)
                listObjects.append(typeObject)
            return listObjects
        except Exception as e:
            return "error in fromExcelToList:"+str(e)
        
    def fromExcelToModel(T, ws):
        try:
            args =[cell.value for cell in ws]
            typeObject = T(*args)
            return typeObject
        except Exception as e:
            return "error in fromExcelToModel:"+str(e)
            
    
    def saveRecord(wb,name, new_data, file_path):
        ws=wb[name]
        ws.append(new_data)
        wb.save(file_path)
     
    def countPatients(self, wb, today, folder_path):
        try: 
            ws = wb['current']
            records = self.fromExcelToList(Record,ws)
        
            for i in  range(2, ws.max_row+1):
                if(records[i-2].patients == -1 or records[i-2].date == today):
                    day_name = records[i-2].date #name of the day and worksheet name
                    men_num=0
                    woman_num=0
                    child_num=0
                    ws_current = wb[day_name] #get to specific day page
                    patients_num = ws_current.max_row-1 #get number of patients that day
                
                    records[i-2].patients = patients_num
                    #if there are patients, then count types
                    if(patients_num!=0):
                        df=pd.read_excel(folder_path, i)#count men woman child
                        mylist = df['М\Ж\Р'].tolist() #get types list
                        #count each type specifically
                        woman_num = mylist.count("Ж") 
                        men_num = mylist.count("М")  
                        child_num = mylist.count("Р")  
                        #save to records list
                        records[i-2].child = child_num
                        records[i-2].woman = woman_num
                        records[i-2].men = men_num
                        #save all info           
                        ws.cell(row=i, column=2).value = patients_num
                        ws.cell(row=i, column=3).value = child_num
                        ws.cell(row=i, column=4).value = woman_num
                        ws.cell(row=i, column=5).value = men_num
        except Exception as e:
            return "error in countPatients:"+str(e)
       
        wb.save(folder_path) #update excel file
        return records
   
    def isAlredySaved(id, name, birthday, file):
        try:
            #to get list of saved names and birthdays
            df=pd.read_excel(file, id) 
            name_list = df["ФИО пациента"].tolist() 
        
            if(name in name_list): # check if name already exists
                return True
            else:
                return False  
        except Exception as e:
            return "error in isAlredySaved:"+str(e) 
        
    def checkSavePatientGetPage(self,
                                id,
                                patient_id, 
                                patient_name, 
                                patient_type, 
                                patient_birthdate, 
                                patient_reason,
                                patient_pressure,
                                patient_doc,
                                patient_docId,
                                file,
                                folder):
        try:
            patient_time = datetime.now()
            wb = self.getWB(file)
            isNotUnique = self.isAlredySaved(id, patient_name, patient_birthdate, file)
            if(isNotUnique):
                return ("/day/"+id+"/1/"+patient_name)
            elif (id in wb.sheetnames):
                new_data = [patient_id, patient_time, patient_name,patient_doc, int(patient_docId), patient_type, patient_birthdate, patient_reason, patient_pressure]
                self.formFileSave(self, id, patient_id, patient_name, patient_pressure, patient_birthdate, patient_reason, patient_doc, folder)
                self.saveRecord(wb, id, new_data, file)
                return ("/day/"+id)
            else:
                return ("/")  
        except Exception as e:
            return "error in checkSavePatientGetPage:"+str(e)  
    
    def formFileSave(self, id, patient_id, patient_name, patient_pressure, patient_bday, patient_reason, doctor_name, folder):
        template = "records/form.docx"
        document = MailMerge(template)
        document.merge(
          date = '{:%d-%b-%Y}'.format(date.today()),
          condition = patient_reason,
          patientBday = patient_bday,
          doctorAssistant = "assistant",
          doctorSpec = "spec",
          patientPressure = patient_pressure,
          doctorName = doctor_name,
          patientName = patient_name,
          number =  patient_id
        )
        p_name = patient_name.replace(" ", "_")
        ##form path to folder:
        doc = os.path.join(folder,patient_id+'.'+doctor_name+'_('+p_name+').docx')
        print('here')
        document.write(doc)
    
    def countGrownUp():
        yrs = date.today()  - relativedelta(years=18)  
        return str(yrs)  
    def countCentury():
        yrs = date.today()  - relativedelta(years=100)  
        return str(yrs)          
              
    def getDocName(self, id, file):
        try:
            wb = self.getWB(file)    
            wsDoc = wb["settings"]
            docName = wsDoc[id][1].value
            #docSpec = wsDoc[id][2].value
            return docName
        except Exception as e:
            return "error in getDocName:"+str(e) 

    def sortDoctors (docs, patient):
        for doc in docs:
            id = doc.id
            sorted_docs=[p for p in patient if p.docId == id]
            doc.num = len(sorted_docs)
        return docs
        
    
            
    
    
        
                
         
        
    


