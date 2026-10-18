from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.realdata.store import RealDataStore


@contextmanager
def fake_connection_context(connection):
    yield connection


def configured_connection():
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = False
    return connection, cursor


def test_register_uses_cursor_executemany_for_psycopg3() -> None:
    connection, cursor = configured_connection()
    manifest = {
        "dataset_id": "rieth-tep-2017",
        "title": "TEP",
        "persistent_id": "doi:10.7910/DVN/6C3JR1",
        "repository": "Harvard Dataverse",
        "license": "CC0",
    }
    tags = [{
        "canonical_tag": "TEP.XMEAS.01",
        "source_column": "xmeas_1",
        "kind": "measurement",
        "description": "A feed",
        "unit": "kscmh",
    }]

    with patch("app.realdata.store.psycopg.connect", return_value=fake_connection_context(connection)):
        RealDataStore("postgresql://test").register(manifest, tags)

    connection.executemany.assert_not_called()
    cursor.executemany.assert_called_once()


def test_observation_batch_uses_cursor_executemany() -> None:
    connection, cursor = configured_connection()
    rows = [("dataset", "split", 0, 1, 1, 180, "TEP.XMEAS.01", 1.2, "abc")]

    with patch("app.realdata.store.psycopg.connect", return_value=fake_connection_context(connection)):
        RealDataStore("postgresql://test").write_long(rows)

    connection.executemany.assert_not_called()
    cursor.executemany.assert_called_once()
    assert cursor.executemany.call_args.args[1] == rows


def test_no_connection_executemany_remains_in_store() -> None:
    source = (Path(__file__).parents[2] / "app" / "realdata" / "store.py").read_text()
    assert "connection.executemany" not in source
    assert "cursor.executemany" in source
