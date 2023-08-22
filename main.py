from fastapi import FastAPI, Body, Path, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from starlette.requests import Request
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
import pymongo
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()
app.title = "Terroristas"

cluster = pymongo.MongoClient('mongodb+srv://admin:admin123@cluster0.7fnfgrt.mongodb.net/?retryWrites=true&w=majority')

db = cluster['Interpol']

terroristas_collection = db['terroristas']


class Terrorista(BaseModel):
    id: int
    nombre: str
    edad: int
    afiliaciones: str
    pasatiempos: str
    nacionalidad: str
    paises_buscados: int


@app.get("/",tags=['Home'])
async def root():
    return {"message": "Hello World"}

@app.post("/terroristas/", response_model=Terrorista, tags=['Terroristas'])
def register_terrorist(terrorista: Terrorista) -> Terrorista:
    terrorista_data = terrorista.dict()
    inserted_terrorist = terroristas_collection.insert_one(terrorista_data)
    terrorista.id = str(inserted_terrorist.inserted_id)
    return JSONResponse(content=jsonable_encoder(terrorista), status_code=200)
    
@app.get("/terroristas/", tags=["Terroristas"], response_model=List[Terrorista])
def get_terroristas() -> List[Terrorista]:
    terroristas = list(terroristas_collection.find({}))
    if terroristas:
        for terrorista in terroristas:
            terrorista["_id"] = str(terrorista["_id"])
        return JSONResponse(content=terroristas, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin terroristas encontrados"}, status_code=404)

@app.delete('/terroristas/{id}', tags=['Terroristas'], status_code=200, response_model=Terrorista)
def delete_terrorist(id: str) -> JSONResponse:
    terrorist = terroristas_collection.find_one_and_delete({"_id": ObjectId(id)})
    if terrorist:
        deleted_terrorist = Terrorista(**terrorist)
        return JSONResponse(content=deleted_terrorist.dict(), status_code=200)
    else:
        raise JSONResponse(content={"message":"Terroristas no encontrado"}, status_code=404)
    
@app.put('/terroristas/{id}', tags=['Terroristas'], status_code=200, response_model=Terrorista)
def update_terrorist(id: str, updated_terrorist: Terrorista) -> JSONResponse:
    existing_terrorist = terroristas_collection.find_one({"_id": ObjectId(id)})
    if existing_terrorist:
        updated_values = updated_terrorist.dict()
        terroristas_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_values})
        
        updated_terrorist._id = ObjectId(id)
        return JSONResponse(content=updated_terrorist.dict(), status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Terrorista no encontrado")