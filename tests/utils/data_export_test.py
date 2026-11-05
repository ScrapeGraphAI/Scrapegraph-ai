import csv

from scrapegraphai.utils.data_export import export_to_csv


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_export_to_csv_writes_rows(tmp_path):
    path = tmp_path / "out.csv"
    export_to_csv([{"name": "a", "price": 1}, {"name": "b", "price": 2}], str(path))

    fieldnames, rows = read_csv(path)
    assert fieldnames == ["name", "price"]
    assert rows == [{"name": "a", "price": "1"}, {"name": "b", "price": "2"}]


def test_export_to_csv_rows_with_different_keys(tmp_path):
    path = tmp_path / "out.csv"
    data = [
        {"name": "a", "price": 1},
        {"name": "b", "price": 2, "rating": 4.5},
        {"name": "c"},
    ]

    export_to_csv(data, str(path))

    fieldnames, rows = read_csv(path)
    assert fieldnames == ["name", "price", "rating"]
    assert rows == [
        {"name": "a", "price": "1", "rating": ""},
        {"name": "b", "price": "2", "rating": "4.5"},
        {"name": "c", "price": "", "rating": ""},
    ]


def test_export_to_csv_empty_data_writes_nothing(tmp_path):
    path = tmp_path / "out.csv"
    export_to_csv([], str(path))
    assert not path.exists()
