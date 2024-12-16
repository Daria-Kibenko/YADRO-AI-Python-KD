from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_substructure_search():
    response = client.post("/molecule/", json={"smiles": "CCO"})
    assert response.status_code == 200
    molecule_id = response.json()["id"]

    response = client.post("/molecule/", json={"smiles": "c1ccccc1"})
    assert response.status_code == 200

    response = client.post("/substructure/", json={"smiles": "c1ccccc1"})
    assert response.status_code == 200
    assert "c1ccccc1" in response.json()["matched_molecules"]
