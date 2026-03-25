from rest_framework.response import Response
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def api_response(status, message, data=None, status_code=200):
    response_data = {
        "status": status,
        "message": message,
        "data": data
    }
    return Response(response_data, status=status_code)

def generate_event_qr(event):
    if not event.qr_code_token:
        event.qr_code_token = str(uuid.uuid4())
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(event.qr_code_token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f'qr_{event.id}.png'
    
    # Save the file to the field
    event.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=True)
    # event.save() # Avoid recursion or redundancy if save=True is used
