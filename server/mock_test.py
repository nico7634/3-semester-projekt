import pytest
from unittest.mock import Mock
from postgres.Postgres_Class import PostgresClass

@pytest.fixture
def mock_postgres():
    # Lav PostgresClass objekt
    pg = PostgresClass("user", "pass", "host", "5432", "db")

    # Mock cursor og connection med Mock i stedet for MagicMock
    pg.cursor = Mock()
    pg.conn = Mock()
    return pg

def test_add_value(mock_postgres):
    # Kald add_value
    mock_postgres.add_value("sensor1", 42)

    # Tjek at execute blev kaldt med noget der indeholder 'INSERT'
    assert "INSERT" in mock_postgres.cursor.execute.call_args[0][0]

    # Tjek at commit blev kaldt
    mock_postgres.conn.commit.assert_called_once()

def test_fetch_one_value(mock_postgres):

    mock_postgres.cursor.fetchone.return_value = [55]
    result = mock_postgres.fetch_one_value("sensor1", "db")
    assert result == 55

def test_fetch_one_row(mock_postgres):

    mock_postgres.cursor.fetchone.return_value = [42]
    result = mock_postgres.fetch_one_row("sensor1", "db")
    assert result == 42

def test_create_sensor_table_valid(mock_postgres):
    mock_postgres.create_sensor_table("sensor1")

    mock_postgres.cursor.execute.assert_called()
    mock_postgres.conn.commit.assert_called()
