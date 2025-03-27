from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_chart_corrections(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    corrections = {}

    for page in doc:
        text = page.get_text()
        if "INDEX OF CHARTS AFFECTED" not in text.upper():
            continue

        lines = text.splitlines()
        for line in lines:
            # Expect lines like: 1467       1568T, 1570
            match = re.match(r"^\s*(\d{1,4})\s+([\dTP ,]+)$", line.strip())
            if match:
                chart = match.group(1)
                notices_raw = match.group(2)
                notices = [n.strip() for n in re.split(r",|\s+", notices_raw) if n.strip()]
                if chart not in corrections:
                    corrections[chart] = []
                corrections[chart].extend(notices)

    return corrections

@app.route("/parse", methods=["POST"])
def parse_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    pdf_file = request.files["file"]
    result = extract_chart_corrections(pdf_file)
    return jsonify(result)

@app.route("/", methods=["GET"])
def hello():
    return "SNII Parser is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
