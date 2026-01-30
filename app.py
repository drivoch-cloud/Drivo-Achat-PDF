from flask import Flask, request, jsonify, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os

app = Flask(__name__)

FILES_DIR = "/tmp/files"
os.makedirs(FILES_DIR, exist_ok=True)


@app.post("/pdf")
def pdf():
    data = request.get_json(force=True)

    text = data.get("text", "")
    numero = data.get("numero_matricule", "000.000.000")
    car = data.get("car", "Car")
    car_type = data.get("type", "Type")

    filename = f"{numero} ACHAT {car} {car_type}.pdf"

    file_id = str(uuid.uuid4())
    path = os.path.join(FILES_DIR, f"{file_id}.pdf")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    x, y = 40, h - 50
    c.setFont("Helvetica", 10)

    for line in text.splitlines():
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = h - 50

        if line.strip() == "":
            y -= 10
        else:
            c.drawString(x, y, line)
            y -= 14

    c.save()
    buf.seek(0)

    with open(path, "wb") as f:
        f.write(buf.read())

    return jsonify({
        "url": f"/download/{file_id}",
        "filename": filename
    })


@app.get("/download/<file_id>")
def download(file_id):
    path = os.path.join(FILES_DIR, f"{file_id}.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404

    return send_file(path, as_attachment=True,
                     download_name=request.args.get("filename", "contrat.pdf"))
