from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from rdkit import Chem

from task_1 import substructure_search

app = FastAPI()

# In-memory storage for molecules
molecule_db = {}


class Molecule(BaseModel):
    smiles: str


class MoleculeUpdate(BaseModel):
    smiles: Optional[str]


@app.post("/molecule/")
def add_molecule(molecule: Molecule):
    # Generate a unique identifier for the molecule
    molecule_id = str(uuid4())
    molecule_db[molecule_id] = molecule.smiles
    return {"id": molecule_id}


@app.get("/molecule/{molecule_id}")
def get_molecule(molecule_id: str):
    if molecule_id not in molecule_db:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return {"id": molecule_id, "smiles": molecule_db[molecule_id]}


@app.put("/molecule/{molecule_id}")
def update_molecule(molecule_id: str, molecule: MoleculeUpdate):
    if molecule_id not in molecule_db:
        raise HTTPException(status_code=404, detail="Molecule not found")

    # Update the molecule if a new SMILES string is provided
    if molecule.smiles is not None:
        molecule_db[molecule_id] = molecule.smiles

    return {"id": molecule_id, "smiles": molecule_db[molecule_id]}


@app.delete("/molecule/{molecule_id}")
def delete_molecule(molecule_id: str):
    if molecule_id not in molecule_db:
        raise HTTPException(status_code=404, detail="Molecule not found")
    del molecule_db[molecule_id]
    return {"message": "Molecule deleted"}


@app.get("/molecules/")
def list_molecules():
    return [{"id": id, "smiles": smiles} for id, smiles in molecule_db.items()]


@app.post("/substructure/")
def substructure_search_endpoint(substructure: Molecule):
    molecules = list(molecule_db.values())
    matched_molecules = substructure_search(molecules, substructure.smiles)
    return {"matched_molecules": matched_molecules}
