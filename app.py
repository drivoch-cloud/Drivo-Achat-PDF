from flask import Flask, request, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.post("/pdf")
def pdf():
    data = request.get_json(force=True)
    filename = data.get("filename", "contrat.pdf")
    text = data["text"]

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    x, y = 40, h - 50

    for line in text.splitlines():
        if y < 50:
            c.showPage()
            y = h - 50
        c.drawString(x, y, line[:120])
        y -= 14

    c.save()
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )

@app.get("/health")
def health():
    return {"ok": True}
