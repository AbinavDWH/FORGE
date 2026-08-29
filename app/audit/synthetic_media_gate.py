import io

from PIL import Image

# Typical diffusion-generator output sizes.
GENERATOR_TYPICAL_DIMENSIONS = {
    (1024, 1024), (1152, 896), (896, 1152), (1216, 832), (832, 1216),
    (1344, 768), (768, 1344), (1536, 672), (672, 1536),
}


def _c2pa_detected(raw: bytes) -> bool:
    return b"c2pa" in raw or b"jumb" in raw or b"ContentCredentials" in raw


def screen_image(raw: bytes) -> dict:
    """
    Local AI-generation screening. One more confidence signal -
    it never claims 100% certainty.
    """
    checks = []
    exif_present = False
    make_model = False
    dimensions = None

    try:
        img = Image.open(io.BytesIO(raw))
        dimensions = img.size
        exif = img.getexif()
        exif_present = bool(exif)
        make_model = bool(exif.get(0x010F) or exif.get(0x0110))
    except Exception:
        checks.append("unreadable image")

    c2pa = _c2pa_detected(raw)
    gen_dims = dimensions in GENERATOR_TYPICAL_DIMENSIONS

    checks.append("camera EXIF present" if exif_present else "no EXIF metadata")
    checks.append(
        "camera make/model signature present"
        if make_model
        else "no camera make/model signature"
    )
    if c2pa:
        checks.append("C2PA / Content Credentials manifest detected")
    if gen_dims:
        checks.append(f"generator-typical dimensions {dimensions}")

    risk_points = 0
    if c2pa:
        risk_points += 2
    if not exif_present:
        risk_points += 1
    if not make_model:
        risk_points += 1
    if gen_dims:
        risk_points += 1

    if risk_points >= 3:
        risk = "high"
    elif risk_points >= 1:
        risk = "medium"
    else:
        risk = "low"

    return {
        "ai_generation_risk": risk,
        "c2pa_detected": c2pa,
        "exif_present": exif_present,
        "make_model_present": make_model,
        "dimensions": list(dimensions) if dimensions else None,
        "checks": checks,
    }