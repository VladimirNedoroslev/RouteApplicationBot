from io import BytesIO

import qrcode


def get_qrcode_from_string(string):
    image = qrcode.make(string)
    qr_code = BytesIO()
    qr_code.name = 'qr_code.jpeg'
    image.save(qr_code, 'JPEG')
    qr_code.seek(0)
    return qr_code
