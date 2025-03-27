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
            current_chart = None

            for line in lines:
                line = line.strip().replace('\u2007', '').replace('\uf0b7', '')
                tokens = re.split(r"[ ,\t]+", line)

                for token in tokens:
                    if re.match(r"^\d{1,4}(?:_\d{1,2})?$", token):
                        current_chart = token
                        if current_chart not in corrections:
                            corrections[current_chart] = []
                    elif re.match(r"^\d+[TP]?$", token) and current_chart:
                        corrections[current_chart].append(token)
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
