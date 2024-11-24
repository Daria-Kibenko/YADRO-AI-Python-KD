from msilib.schema import File

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import uuid
from rdkit import Chem
from rdkit.Chem import Draw

# Инициализация приложения
app = FastAPI()


# Модель молекулы
class Molecule(BaseModel):
    smiles: str
    identifier: Optional[str] = None  # Идентификатор генерируется, если не передан


# Модель для обновления молекулы
class MoleculeUpdate(BaseModel):
    smiles: Optional[str] = None  # Только для обновления SMILES


# Модель для ответа поиска подструктуры
class SubstructureSearchResponse(BaseModel):
    matched_molecules: List[str]


# Временное хранилище молекул (в памяти)
molecules_db = {}


# Функция для поиска подструктуры
def substructure_search(molecules: List[str], substructure: str) -> List[str]:
    substructure_mol = Chem.MolFromSmiles(substructure)
    if not substructure_mol:
        raise ValueError("Invalid substructure SMILES string")

    matched_molecules = []
    for mol_smiles in molecules:
        mol = Chem.MolFromSmiles(mol_smiles)
        if mol and mol.HasSubstructMatch(substructure_mol):
            matched_molecules.append(mol_smiles)

    return matched_molecules


# API маршруты

@app.post("/molecules/")
def add_molecule(molecule: Molecule):
    if not molecule.identifier:
        molecule.identifier = str(uuid.uuid4())

    if molecule.identifier in molecules_db:
        raise HTTPException(status_code=400, detail="Molecule already exists")

    molecules_db[molecule.identifier] = molecule
    return {"message": "Molecule added", "identifier": molecule.identifier}


@app.get("/molecules/{identifier}")
def get_molecule(identifier: str):
    molecule = molecules_db.get(identifier)
    if not molecule:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return molecule


@app.put("/molecules/{identifier}")
def update_molecule(identifier: str, molecule_update: MoleculeUpdate):
    molecule = molecules_db.get(identifier)
    if not molecule:
        raise HTTPException(status_code=404, detail="Molecule not found")

    if molecule_update.smiles:
        molecule.smiles = molecule_update.smiles
    return {"message": "Molecule updated", "molecule": molecule}


@app.delete("/molecules/{identifier}")
def delete_molecule(identifier: str):
    if identifier in molecules_db:
        del molecules_db[identifier]
        return {"message": "Molecule deleted"}
    else:
        raise HTTPException(status_code=404, detail="Molecule not found")


@app.get("/molecules/", response_model=List[Molecule])
def list_molecules():
    return list(molecules_db.values())


@app.get("/molecules/search/", response_model=SubstructureSearchResponse)
def search_molecules(substructure: str):
    all_molecules = [molecule.smiles for molecule in molecules_db.values()]

    try:
        matched_molecules = substructure_search(all_molecules, substructure)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"matched_molecules": matched_molecules}


@app.post("/molecules/upload/")
async def upload_molecules(file: UploadFile = File(...)):
    content = await file.read()
    smiles_list = content.decode("utf-8").splitlines()

    added_molecules = []
    for smiles in smiles_list:
        molecule = Molecule(smiles=smiles, identifier=str(uuid.uuid4()))
        molecules_db[molecule.identifier] = molecule
        added_molecules.append(molecule)

    return {"message": f"{len(added_molecules)} molecules uploaded"}
