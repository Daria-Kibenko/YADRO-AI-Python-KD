from rdkit import Chem


def substructure_search(molecules, substructure):
    substructure_molecule = Chem.MolFromSmiles(substructure)

    if substructure_molecule is None:
        raise ValueError("Invalid substructure SMILES")

    result = []
    for mol_smiles in molecules:
        mol = Chem.MolFromSmiles(mol_smiles)
        if mol is None:
            continue

        if mol.HasSubstructMatch(substructure_molecule):
            result.append(mol_smiles)

    return result
