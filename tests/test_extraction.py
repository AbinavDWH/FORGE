from app.extraction.structurer import structure_text
from app.api.extraction import extract_fields, ExtractionRequest


def test_structure_text_concrete_pouring_completed():
    raw = "Sector B Pier 14 concrete pouring completed"
    result = structure_text(raw)
    assert result["spatial_zone"] == "Zone B"
    assert result["discipline"] == "Civil"
    assert result["component"] == "Pier 14"
    assert result["action"] == "Concrete pouring"
    assert result["status"] == "Completed"
    assert result["percent_complete"] == 100


def test_structure_text_partial_progress():
    raw = "Zone A Pier 12 concrete pouring 60%"
    result = structure_text(raw)
    assert result["spatial_zone"] == "Zone A"
    assert result["discipline"] == "Civil"
    assert result["component"] == "Pier 12"
    assert result["percent_complete"] == 60
    assert result["status"] == "In Progress"


def test_structure_text_piping_hydro_test():
    raw = "Line 2 hydro testing completed"
    result = structure_text(raw)
    assert result["discipline"] == "Piping"
    assert result["action"] == "Hydro testing"
    assert result["status"] == "Completed"
    assert result["percent_complete"] == 100


def test_structure_text_does_not_invent_missing_fields():
    raw = "Just checking the weather today"
    result = structure_text(raw)
    assert result["spatial_zone"] is None
    assert result["component"] is None
    assert result["discipline"] is None
    assert result["action"] is None
    assert result["status"] is None
    assert result["percent_complete"] is None


def test_extract_fields_endpoint():
    req = ExtractionRequest(ingestion_id="ING-9999", raw_text="Sector B Pier 14 concrete pouring done")
    res = extract_fields(req)
    assert res.ingestion_id == "ING-9999"
    assert res.spatial_zone == "Zone B"
    assert res.component == "Pier 14"
    assert res.discipline == "Civil"
    assert res.percent_complete == 100
    assert res.extraction_confidence > 0.5
