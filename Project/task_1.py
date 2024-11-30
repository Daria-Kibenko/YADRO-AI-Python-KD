from rdkit import Chem


def substructure_search(molecules, substructure):
    # Convert the substructure into a RDKit molecule
    substructure_molecule = Chem.MolFromSmiles(substructure)

    if substructure_molecule is None:
        raise ValueError("Invalid substructure SMILES")

    result = []
    for mol_smiles in molecules:
        # Convert the molecule into a RDKit molecule
        mol = Chem.MolFromSmiles(mol_smiles)

        if mol is None:
            continue

        # Check if the molecule contains the substructure
        if mol.HasSubstructMatch(substructure_molecule):
            result.append(mol_smiles)

    return result
