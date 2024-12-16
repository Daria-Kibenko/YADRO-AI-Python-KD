from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from uuid import uuid4

from app.celery_worker import celery
from app.models import Molecule as DBMolecule, SessionLocal
from app.tasks import substructure_search_task
import logging
from typing import Optional

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Molecule(BaseModel):
    smiles: str


class MoleculeUpdate(BaseModel):
    smiles: Optional[str]

@app.post("/molecule/")
def add_molecule(molecule: Molecule):
    molecule_id = str(uuid4())
    molecule_db[molecule_id] = molecule.smiles
    logger.info(f"Added molecule {molecule_id} with SMILES: {molecule.smiles}")
    return {"id": molecule_id}


@app.get("/molecules/")
def list_molecules(limit: Optional[int] = 100):
    molecules = list(molecule_db.items())[:limit]
    return [{"id": id, "smiles": smiles} for id, smiles in molecules]


@app.post("/substructure/")
async def substructure_search_endpoint(substructure: Molecule):
    task = substructure_search_task.apply_async(args=[list(molecule_db.values()), substructure.smiles])
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "Task is still processing"}
    elif task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "Task completed", "result": task_result.result}
    else:
        return {"task_id": task_id, "status": task_result.state}
