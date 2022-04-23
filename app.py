import matplotlib
matplotlib.use('Agg')

import os
from sys import path
from flask import Flask, render_template, request,redirect, url_for
from getData import detectImage, face_distance_to_conf
from detectDriversLicense import getDriversLicense
from residenceCard import getResidenceCard
from detectMyNumber import getMyNumber
from passport import getPassport
from insuranceCard1 import getInsuranceCatd


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/check', methods=["GET", "POST"])
def check():
    

    image1 = request.files["image1"]
    image2 = request.files["image2"]
    messages = ""
    type = str(request.form["type"])
    if image1.filename == '' or image2.filename == '':
        return render_template("index.html")

    path1 = os.path.join(app.config['UPLOAD_FOLDER'], image1.filename)
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], image2.filename)

    
    image1.save(path1)
    image2.save(path2)

    result_from_detect = detectImage(path1,path2)
    linear_val = (1.0 - result_from_detect[1]) / (0.8)

    accuracy ='{percent:.2%}'.format(percent=face_distance_to_conf(result_from_detect[1]))
    # "1":運転免許証
    # "2":パスポート
    # "3":マイナンバー
    # "4":在留カード 
    # "5":保険証 
    if(type == "1"): 
        messages =  getDriversLicense(path1)
    elif(type == "2"): 
        messages =  getPassport(path1)
    elif(type == "3"):
        messages =  getMyNumber(path1) 
    elif(type == "4"): 
        messages =  getResidenceCard(path1) 
    elif(type == "5"): 
        messages =  getInsuranceCatd(path1)
    if result_from_detect[2]:
        os.remove(path1)
        os.remove(path2)
        return render_template("index.html",message="写真がぼやけてしまいまして、もう一度やり直してください")
    else:

        if result_from_detect[0]:

            return render_template("index.html", result="一致する",accuracy="同じ : " + accuracy,path1 = path1,path2=path2,messages=messages)
        else:
            return render_template("index.html", result="一致しない",accuracy="同じ : " + accuracy,path1 = path1,path2=path2,messages=messages)


@app.route('/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename=filename), code=301)


@app.route('/clear', methods=["GET", "POST"])
def clear():

    path1 = request.form["path1"]
    path2 = request.form["path2"]
    if path1 != "":
        os.remove(path1)
    if path2 != "":
        os.remove(path2)
    return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

