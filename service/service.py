import os
import openpyxl
from datetime import date, datetime
from typing import TypeVar
import pandas as pd
from dateutil.relativedelta import relativedelta

from model.record import Record

class Service():
    T = TypeVar('T')
    
    def getWB():
        try:
            path=os.path.join("C:", "records/medical.xlsx")
            #path=os.path.join(os.getcwd(), "records/medical.xlsx")
            return openpyxl.load_workbook(path)
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
    
    def saveRecord(wb,name, new_data, fiel_path):
        ws=wb[name]
        ws.append(new_data)
        wb.save(fiel_path)
     
    def countPatients(self, wb, today):
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
                        df=pd.read_excel('records/medical.xlsx', i)#count men woman child
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
                        ws.cell(row=i, column=3).value = patients_num
                        ws.cell(row=i, column=5).value = child_num
                        ws.cell(row=i, column=6).value = woman_num
                        ws.cell(row=i, column=7).value = men_num
        except Exception as e:
            return "error in countPatients:"+str(e)
       
        wb.save("records/medical.xlsx") #update excel file
        return records
   
    def isAlredySaved(id, name, birthday):
        try:
            #to get list of saved names and birthdays
            df=pd.read_excel('records/medical.xlsx', id) 
            name_list = df["ФИО пациента"].tolist() 
            birth_list = df["Дата рождения"].tolist() 
        
            if(name in name_list): # check if name already exists
                index = name_list.index(name)
                if(birth_list[index]==birthday): #check if birthday is the same
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
                                patient_pressure):
        try:
            patient_time = datetime.now()
            wb = self.getWB()
            isUnique = self.isAlredySaved(id, patient_name, patient_birthdate)
            if(isUnique):
                return ("/day/"+id+"/1/"+patient_name)
            elif (id in wb.sheetnames):
                new_data = [patient_id, patient_time, patient_name, patient_type, patient_birthdate, patient_reason, patient_pressure]
                self.saveRecord(wb, id, new_data)
                return ("/day/"+id)
            else:
                return ("/")  
        except Exception as e:
            return "error in checkSavePatientGetPage:"+str(e)  
    
    def countGrownUp():
        yrs = date.today()  - relativedelta(years=18)  
        return str(yrs)  
    def countCentury():
        yrs = date.today()  - relativedelta(years=100)  
        return str(yrs)          
                

    
            
    
    
        
                
         
        
    


