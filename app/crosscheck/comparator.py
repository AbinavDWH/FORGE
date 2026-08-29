from app.crosscheck.normalizer import values_match

# Demo scope per module plan: compare the 3 critical fields.
COMPARE_FIELDS = ["component", "action", "status"]


def compare(ocr_extraction: dict, vlm_extraction: dict) -> dict:
    """
    Field-level OCR vs VLM comparison.
    OCR remains the source of truth, always.
    """
    field_agreement = {}

    for field in COMPARE_FIELDS:
        a = ocr_extraction.get(field)
        b = vlm_extraction.get(field)
        if a is None and b is None:
            field_agreement[field] = "match"
        elif values_match(a, b):
            field_agreement[field] = "match"
        else:
            field_agreement[field] = "mismatch"

    matches = sum(1 for v in field_agreement.values() if v == "match")
    agreement_score = round(matches / len(COMPARE_FIELDS), 2)

    if agreement_score == 1.0:
        status = "agreed"
    elif agreement_score == 0.0:
        status = "disagreed"
    else:
        status = "partial_mismatch"

    return {
        "field_agreement": field_agreement,
        "agreement_score": agreement_score,
        "cross_check_status": status,
        "source_of_truth": "ocr",
        "ocr_extraction": ocr_extraction,
        "vlm_extraction": vlm_extraction,
    }