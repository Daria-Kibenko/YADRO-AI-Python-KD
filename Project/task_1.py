from rdkit import Chem


def substructure_search(molecule_smiles, substructure_smiles):
    """
    This function searches for a substructure (given as a SMILES string) in a list of molecules.

    Parameters:
    - molecule_smiles (list): A list of SMILES strings representing the molecules.
    - substructure_smiles (str): A SMILES string representing the substructure to search for.

    Returns:
    - list: A list of SMILES strings for molecules that contain the substructure.
    """

    # Convert the substructure SMILES string to a molecule object
    substructure = Chem.MolFromSmiles(substructure_smiles)

    # List to hold the matching molecules
    matching_molecules = []

    # Iterate over each molecule SMILES in the input list
    for smiles in molecule_smiles:
        # Convert the molecule SMILES string to a molecule object
        molecule = Chem.MolFromSmiles(smiles)

        # Check if the substructure exists in the molecule
        if molecule and substructure and molecule.HasSubstructMatch(substructure):
            matching_molecules.append(smiles)

    return matching_molecules


molecule_list = ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"]
substructure = "c1ccccc1"
result = substructure_search(molecule_list, substructure)
print(result)
