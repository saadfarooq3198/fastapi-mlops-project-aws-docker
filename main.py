from fastapi import FastAPI, HTTPException,Path,Query
from pydantic import BaseModel, Field,computed_field
from typing import Annotated, Literal
from fastapi.responses import JSONResponse

import json


app = FastAPI()

# Helper Methods
def load_data():
    with open("patients.json", 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
async def hello():
    return {"message": "Patient Management System API"}

@app.get('/view')
def view():
    data = load_data()
    return data
# Pydantic model building for data validation for Post requests
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Id of Patient", example="P004")]
    name: Annotated[str, Field(..., max_length=50, description="Patient Name", example="Saad")]
    city: Annotated[str, Field(..., description="Patient City")]
    age: Annotated[int, Field(..., gt=0, le=120, description="Patient Age")]
    gender: Annotated[ Literal['male', 'female', 'others'], Field(..., description="Patient Gender")]
    height: Annotated[float, Field(..., gt=0, description="Patient Height")]
    weight: Annotated[float, Field(..., gt=0, description="Patient Weight")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

# Path Parameters
@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description = "ID of Patient in DB", example = "P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found in database")

@app.get("/sort")
def sort_patient(sort_by: str = Query(..., description = "sort by height, weight or BMI"), order: str = Query('asc', description = "sort in ascending or descending order")):
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail = "Invalid Field")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail = "Invalid Field")
    data = load_data()
    sort_order = True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by,0), reverse=sort_order)
    return sorted_data

# Post Method
@app.post("/create")
def create_patient(patient: Patient):
    # load existing data
    data = load_data()

    # check if the patient already exist
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exist")
    
    # add new patient
    # convert pydantic object into python dictionary
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save back data into file
    save_data(data)
    return JSONResponse(status_code=201, content={'message': 'Patient Created Successfully'})