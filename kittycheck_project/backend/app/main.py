from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kittycheck.db")

database = Database(DATABASE_URL)
metadata = MetaData()

gatos = Table(
    "gatos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nombre", String, nullable=False),
    Column("edad", Integer, nullable=False),
    Column("peso", Integer, nullable=False)
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI(title="KittyCheck API")

class Gato(BaseModel):
    nombre: str
    edad: int
    peso: int

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "Hola, KittyCheck!"}

@app.get("/gatos")
async def listar_gatos():
    query = gatos.select()
    return await database.fetch_all(query)

@app.post("/gatos")
async def crear_gato(gato: Gato):
    query = gatos.insert().values(nombre=gato.nombre, edad=gato.edad, peso=gato.peso)
    last_record_id = await database.execute(query)
    return {**gato.dict(), "id": last_record_id}
