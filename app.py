from flask import Flask, request, jsonify
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os

app = Flask(__name__)
os.makedirs("files", exist_ok=True)

@app.post("/pdf")
def pdf():
    data = request.get_json(force=True)
    filename = data.get("filename", "contrat.pdf")
    text = data["text"]

    file_id = str(uuid.uuid4())
    path = f"files/{file_id}.pdf"

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    x, y = 40, h - 50

    for line in text.splitlines():
        if y < 50:
            c.showPage()
            y = h - 50
        c.setFont("Helvetica", 10)

if line.strip() == "":
    y -= 10
else:
    c.drawString(x, y, line)
    y -= 14
        y -= 14

    c.save()
    buf.seek(0)

    with open(path, "wb") as f:
        f.write(buf.read())

    return jsonify({
        "url": f"https://drivo-achat-pdf.onrender.com/download/{file_id}",
        "filename": filename
    })

@app.get("/download/<file_id>")
def download(file_id):
    return app.send_static_file(f"../files/{file_id}.pdf")
