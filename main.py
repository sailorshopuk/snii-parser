from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_chart_corrections(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    corrections = {}

    for page in doc:
        text = page.get_text()
        if "INDEX OF CHARTS AFFECTED" in text.upper():
            lines = text.splitlines()
            for line in lines:
                line = line.strip().replace('\u2007', ' ')  # fix weird spaces
                if not line or not re.search(r'\d', line):
                    continue

                # Try splitting the line into two chart-notice groups
                split_line = re.split(r'\s{2,}', line)
                for segment in split_line:
                    parts = re.split(r'\s+', segment, maxsplit=1)
                    if len(parts) != 2:
                        continue
                    chart = parts[0]
                    notice_blob = parts[1]
                    notices = re.split(r'[, ]+', notice_blob)
                    valid_notices = [n for n in notices if re.match(r'^\d+[TP]?$', n)]
                    if valid_notices:
                        corrections.setdefault(chart, []).extend(valid_notices)
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
