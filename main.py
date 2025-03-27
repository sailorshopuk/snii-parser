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

            current_chart = None

            for line in lines:
                # Remove unwanted unicode spaces
                cleaned_line = line.replace("\u2007", " ").strip()

                # Match chart number: e.g. 5600_2 or 902
                chart_match = re.match(r"^(\d{1,4}(?:_\d{1,2})?)\s+(.*)", cleaned_line)
                if chart_match:
                    current_chart = chart_match.group(1)
                    notices_part = chart_match.group(2)

                    # Find all notices in the rest of the line
                    notices = re.findall(r"\d{3,4}[TP]?", notices_part)
                    if notices:
                        corrections[current_chart] = notices

            break  # Done after first matching index page

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
