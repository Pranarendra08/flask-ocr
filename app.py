from flask import Flask, request, jsonify, render_template
import easyocr
import re
import os
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Konfigurasi folder untuk menyimpan file yang diupload
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

reader = easyocr.Reader(['id'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({
             'message': 'No file part in the request',
             'error': True,
             'OCR_result': []
             }), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
             'message': 'No file selected for uploading',
             'error': True,
             'OCR_result': []
             }), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = reader.readtext(file_path, paragraph=True, x_ths=5.0)
        hasil = ''

        for match in text:
                hasil = hasil + match[1] + '\n'
        print(hasil)

        harga = re_harga(hasil)
        toko = re_toko(hasil)
        tanggal = re_tanggal(hasil)
        # result_ocr = [harga, toko, tanggal]
        
        return jsonify({
             'message': 'File successfully uploaded', 
             'error': False,
             'OCR_result': {
                  'harga' : harga,
                  'toko' : toko,
                  'tanggal' : tanggal
             }
            }), 200

def re_harga(text):
      pattern_harga =  r'[TtJ][OO0][TtJ][A4][LlI1].+'
      pattern_digit = r'\d[^a-zA-z]+\d[oO0][oO0]'
      result = ''

      word_harga = re.findall(pattern_harga, text)
      for match in word_harga:
          result += match + '\n'

      digit_harga = re.findall(pattern_digit, result)
      result = digit_harga[0]

      result = (result.replace(',', ''))
      result = (result.replace('.', ''))
      result = (result.replace(' ', ''))
      result = (result.replace('O', '0'))
      result = (result.replace('o', '0'))
      result = int(result)
      return result

def re_toko(text):
      pattern_indomaret = r'[Iil1][Nn][Dd][Oo0][Mm][Aa4][Rr][Ee3][TtJ]'
      result = ''

      word_indomaret = re.findall(pattern_indomaret, text)

      result = word_indomaret[0]
      result = result.replace("i", "I")
      result = result.replace("l", "I")
      result = result.replace("1", "I")
      result = result.replace("n", "N")
      result = result.replace("d", "D")
      result = result.replace("0", "O")
      result = result.replace("o", "O")
      result = result.replace("m", "M")
      result = result.replace("4", "A")
      result = result.replace("r", "R")
      result = result.replace("e", "E")
      result = result.replace("3", "E")
      result = result.replace("J", "T")
      return result

def re_tanggal(text):
      pattern_tanggal = r'[0-3]\d.?[.,]\d\d.?[.,]\d\d'
      result = ''

      word_tanggal = re.findall(pattern_tanggal, text)

      result = word_tanggal[0]
      result = result.replace(".", "/")
      result = result.replace(",", "/")
      result = result.replace(" ", "")

      a = result[:6]
      b = result[6:]
      result = a + '20' + b

      return result

if __name__ == '__main__':
    app.run(debug=True)
