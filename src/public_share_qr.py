import qrcode
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


def generate_sheet_share_qr_code(share_id, sheet_id, lang="en"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{BASE_URL}/consent/{share_id}/{sheet_id}?lang={lang}")
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white")
