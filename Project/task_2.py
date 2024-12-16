from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from uuid import uuid4
from rdkit import Chem
from models import Molecule as DBMolecule, SessionLocal
from task_1 import substructure_search

app = FastAPI()


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
def add_molecule(molecule: Molecule, db: Session = Depends(get_db)):
    db_molecule = DBMolecule(smiles=molecule.smiles)
    db.add(db_molecule)
    db.commit()
    db.refresh(db_molecule)
    return {"id": db_molecule.id}


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
def list_molecules(db: Session = Depends(get_db)):
    molecules = db.query(DBMolecule).all()
    return [{"id": mol.id, "smiles": mol.smiles} for mol in molecules]


@app.post("/substructure/")
def substructure_search_endpoint(substructure: Molecule, db: Session = Depends(get_db)):
    molecules = [mol.smiles for mol in db.query(DBMolecule).all()]
    matched_molecules = substructure_search(molecules, substructure.smiles)
    return {"matched_molecules": matched_molecules}

