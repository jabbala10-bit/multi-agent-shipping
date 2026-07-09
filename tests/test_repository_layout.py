from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_database_assets_live_under_databases():
    assert (ROOT / "databases" / "tools.yaml").is_file()
    assert (ROOT / "databases" / "sql" / "inventory.sql").is_file()
    assert (ROOT / "databases" / "sql" / "shipping.sql").is_file()


def test_product_manuals_live_under_data():
    manuals = sorted((ROOT / "data").glob("P*.pdf"))

    assert len(manuals) == 14
    assert not list((ROOT / "docs").glob("P*.pdf"))


def test_docs_folder_has_no_database_seed_files():
    assert not (ROOT / "docs" / "inventory.sql").exists()
    assert not (ROOT / "docs" / "shipping.sql").exists()
    assert not (ROOT / "docs" / "tools.yaml").exists()
