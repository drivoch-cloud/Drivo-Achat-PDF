from flask import Flask, request, jsonify, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os

app = Flask(__name__)

# Render-safe writable directory
FILES_DIR = "/tmp/files"
os.makedirs(FILES_DIR, exist_ok=True)


def clean_filename_part(value: str) -> str:
    """
    Keep filenames safe across OS/filesystems.
    Allows letters/numbers/spaces and .-_ only.
    """
    if value is None:
        return ""
    value = str(value).strip()
    allowed = set(" .-_")
    return "".join(ch for ch in value if ch.isalnum() or ch in allowed).strip()


def build_contract_filename(numero_matricule: str, car: str, car_type: str) -> str:
    numero = clean_filename_part(numero_matricule) or "000.000.000"
    car_name = clean_filename_part(car) or "Car"
    ctype = clean_filename_part(car_type) or "Type"
    return f"{numero} ACHAT {car_name} {ctype}.pdf"


@app.post("/pdf")
def pdf():
    data = request.get_json(force=True) or {}

    text = data.get("text", "")

    # These should come from your OCR/image parsing or frontend form
    numero_matricule = data.get("numero_matricule", "")
    car = data.get("car", "")
    car_type = data.get("type", "")

    filename = build_contract_filename(numero_matricule, car, car_type)

    file_id = str(uuid.uuid4())
    path = os.path.join(FILES_DIR, f"{file_id}.pdf")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    w, h = A4
    x, y = 40, h - 50

    c.setFont("Helvetica", 10)

    for line in str(text).splitlines():
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

    # Return both the URL + filename. Frontend can download using this.
    return jsonify({
        "file_id": file_id,
        "filename": filename,
        "url": f"/download/{file_id}?filename={filename}"
    })


@app.get("/download/<file_id>")
def download(file_id):
    path = os.path.join(FILES_DIR, f"{file_id}.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404

    filename = request.args.get("filename", "contrat.pdf")
    filename = clean_filename_part(filename)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    return send_file(path, as_attachment=True, download_name=filename)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})
