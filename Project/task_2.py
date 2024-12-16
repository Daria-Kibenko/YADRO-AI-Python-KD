from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4
from app.models import Molecule as DBMolecule, SessionLocal
import logging
from typing import Optional
from app.tasks import substructure_search_task

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Dependency to get the SQLAlchemy session
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


@app.get("/molecule/{molecule_id}")
def get_molecule(molecule_id: int, db: Session = Depends(get_db)):
    db_molecule = db.query(DBMolecule).filter(DBMolecule.id == molecule_id).first()
    if db_molecule is None:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return {"id": db_molecule.id, "smiles": db_molecule.smiles}


@app.put("/molecule/{molecule_id}")
def update_molecule(molecule_id: int, molecule: MoleculeUpdate, db: Session = Depends(get_db)):
    db_molecule = db.query(DBMolecule).filter(DBMolecule.id == molecule_id).first()
    if db_molecule is None:
        raise HTTPException(status_code=404, detail="Molecule not found")

    if molecule.smiles:
        db_molecule.smiles = molecule.smiles
        db.commit()
        db.refresh(db_molecule)

    return {"id": db_molecule.id, "smiles": db_molecule.smiles}


@app.delete("/molecule/{molecule_id}")
def delete_molecule(molecule_id: int, db: Session = Depends(get_db)):
    db_molecule = db.query(DBMolecule).filter(DBMolecule.id == molecule_id).first()
    if db_molecule is None:
        raise HTTPException(status_code=404, detail="Molecule not found")

    db.delete(db_molecule)
    db.commit()
    return {"message": "Molecule deleted"}


@app.get("/molecules/")
def list_molecules(limit: Optional[int] = 100):
    # Creating an iterator to handle large lists of molecules
    molecules = list(molecule_db.items())[:limit]  # Limit the number of molecules
    return [{"id": id, "smiles": smiles} for id, smiles in molecules]


@app.post("/substructure/")
async def substructure_search_endpoint(substructure: Molecule):
    # Start the substructure search task asynchronously
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