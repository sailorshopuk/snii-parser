from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_chart_corrections(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    corrections = {}

    for i in range(len(doc)):
        text = doc[i].get_text()
        if "INDEX OF CHARTS AFFECTED" in text.upper():
            lines = text.splitlines()
            # Clean and extract numeric tokens
            tokens = []
            for line in lines:
                cleaned = line.strip().replace('\u2007', '')
                if re.match(r"^[\d_]+[TP]?$", cleaned):
                    tokens.append(cleaned)

            # Group into chart → notice pairs
            for j in range(0, len(tokens) - 1, 2):
                chart = tokens[j]
                notice = tokens[j + 1]
                if chart not in corrections:
                    corrections[chart] = []
                corrections[chart].append(notice)
            break  # stop after first matching page

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
