from application import app, dropzone
from flask import render_template, request, redirect, url_for, session , jsonify
from .forms import QRCodeData
import secrets
import os
import base64

# OCR
import cv2
import pytesseract
from PIL import Image
import numpy as np
# pip install gTTS
from gtts import gTTS

# import utils
from . import utils


@app.route("/")
def index():
    return render_template("index.html")
    

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':

        # set a session value
        sentence = ""
        
        f = request.files.get('file')

        filename, extension = f.filename.split(".")
        generated_filename = secrets.token_hex(10) + f".{extension}"
       

        file_location = os.path.join(app.config['UPLOADED_PATH'], generated_filename)

        f.save(file_location)

        # print(file_location)

        # OCR here
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rohit\AppData\Local\Programs\Tesseract-OCR\tesseract'

        img = cv2.imread(file_location)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        languages = [
    'afr', 'amh', 'ara', 'asm', 'aze', 'aze_cyrl', 'bel', 'ben', 'bod', 'bos',
    'bre', 'bul', 'cat', 'ceb', 'ces', 'chi_sim', 'chi_tra', 'chr', 'cym', 'dan',
    'deu', 'div', 'dzo', 'ell', 'eng', 'enm', 'epo', 'est', 'eus', 'fas', 'fin',
    'fra', 'frk', 'frm', 'gle', 'glg', 'grc', 'guj', 'hat', 'heb', 'hin', 'hrv',
    'hun', 'iku', 'ind', 'isl', 'ita', 'ita_old', 'jav', 'jpn', 'kan', 'kat',
    'kat_old', 'kaz', 'khm', 'kir', 'kor', 'kur', 'kur_ara', 'lao', 'lat', 'lav',
    'lit', 'mal', 'mar', 'mkd', 'mlt', 'msa', 'mya', 'nep', 'nld', 'nno', 'nob',
    'oci', 'ori', 'osd', 'pan', 'pol', 'por', 'pus', 'ron', 'rus', 'san', 'sin',
    'slk', 'slv', 'sqi', 'srp', 'srp_latn', 'swa', 'swe', 'syr', 'tam', 'tel',
    'tgk', 'tgl', 'tha', 'tir', 'tur', 'uig', 'ukr', 'urd', 'vie', 'yid', 'yor'
]
        lang_parameter = '+'.join(languages)

        boxes = pytesseract.image_to_data(img,lang='eng+tel+hin+ben+chi_sim')
        # print(boxes)
    
        for i, box in enumerate(boxes.splitlines()):
            if i == 0:
                continue

            box = box.split()
            # print(box)

            # only deal with boxes with word in it.
            if len(box) == 12:
                sentence += box[11] + " "
       
        print(sentence)
        session["sentence"] = sentence

        # delete file after you are done working with it
        os.remove(file_location)

        return redirect("/decoded/")

    else:
       return render_template("upload.html", title="Home")


@app.route("/decoded", methods=["GET", "POST"])
def decoded():

    sentence = session.get("sentence")
    form =QRCodeData() 
    # print(sentence)

    # print(lang)
    translate_to = form.language.data
    a,b=utils.detect_language(sentence)
    lang= translate_to if translate_to else a
    

    

    if request.method == "POST":
        generated_audio_filename = secrets.token_hex(10) + ".mp4"
        text_data = form.data_field.data
        translate_to = form.language.data
        # print("Data here", translate_to)

  
        translated_text = utils.translate_text(text_data, translate_to)
        print(translated_text)
        tts = gTTS(translated_text, lang=translate_to)



        file_location = os.path.join(
                            app.config['AUDIO_FILE_UPLOAD'], 
                            generated_audio_filename
                        )

        # save file as audio
        tts.save(file_location)

        # return redirect("/audio_download/" + generated_audio_filename)

        form.data_field.data = translated_text

        return render_template("decoded.html", 
                        title="Decoded", 
                        form=form, 
                        lang=utils.languages.get(lang),
                        audio = True,
                        file = generated_audio_filename
                    )


    # form.data_field.data = sentence
    form.data_field.data = sentence

    # set the sentence back to defautl blank
    # sentence = ""
    session["sentence"] = ""

    return render_template("decoded.html", 
                            title="Decoded", 
                            form=form, 
                            lang=utils.languages.get(lang),
                            audio = False
                        )

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route('/store_image', methods=["GET",'POST'])
def store_image():
    # set a session value
    sentence = ""

    image_data = request.json.get('image')
    if image_data:
        image_parts = image_data.split(";base64,")
        image_type_aux = image_parts[0].split("image/")
        image_type = image_type_aux[1]
        image_base64 = base64.b64decode(image_parts[1])
        file_name = secrets.token_hex(10) + f".{image_type}"
        file_location = os.path.join(app.config['UPLOADED_PATH'], file_name)
        with open(file_location, 'wb') as file:
            file.write(image_base64)
        print('hi')
            # OCR here
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rohit\AppData\Local\Programs\Tesseract-OCR\tesseract'

        img = cv2.imread(file_location)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        languages = [
            'afr', 'amh', 'ara', 'asm', 'aze', 'aze_cyrl', 'bel', 'ben', 'bod', 'bos',
            'bre', 'bul', 'cat', 'ceb', 'ces', 'chi_sim', 'chi_tra', 'chr', 'cym', 'dan',
            'deu', 'div', 'dzo', 'ell', 'eng', 'enm', 'epo', 'est', 'eus', 'fas', 'fin',
            'fra', 'frk', 'frm', 'gle', 'glg', 'grc', 'guj', 'hat', 'heb', 'hin', 'hrv',
            'hun', 'iku', 'ind', 'isl', 'ita', 'ita_old', 'jav', 'jpn', 'kan', 'kat',
            'kat_old', 'kaz', 'khm', 'kir', 'kor', 'kur', 'kur_ara', 'lao', 'lat', 'lav',
            'lit', 'mal', 'mar', 'mkd', 'mlt', 'msa', 'mya', 'nep', 'nld', 'nno', 'nob',
            'oci', 'ori', 'osd', 'pan', 'pol', 'por', 'pus', 'ron', 'rus', 'san', 'sin',
            'slk', 'slv', 'sqi', 'srp', 'srp_latn', 'swa', 'swe', 'syr', 'tam', 'tel',
            'tgk', 'tgl', 'tha', 'tir', 'tur', 'uig', 'ukr', 'urd', 'vie', 'yid', 'yor'
        ]
        lang_parameter = '+'.join(languages)

        boxes = pytesseract.image_to_data(img,lang='eng+tel+hin+ben')
        # print(boxes)
    
        for i, box in enumerate(boxes.splitlines()):
            if i == 0:
                continue

            box = box.split()
            # print(box)

            # only deal with boxes with word in it.
            if len(box) == 12:
                sentence += box[11] + " "
       
        print(sentence)
        session["sentence"] = sentence

        # delete file after you are done working with it
        os.remove(file_location)
        return jsonify({"message": "Image uploaded successfully."}), 200
    else:
        return jsonify({"error": "No image data provided."}), 400
