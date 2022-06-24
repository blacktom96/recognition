import os
from sys import path
from flask import Flask, render_template, request,redirect, url_for,jsonify
from flask_cors import CORS
from google.cloud import vision
import io

from getData import detectImage, face_distance_to_conf
from detectDriversLicense import getDriversLicense
from residenceCard import getResidenceCard
from detectMyNumber import getMyNumber
from passport import getPassport
from insuranceCard1 import getInsuranceCatd


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = '/var/www/html/recognition/static/uploads/'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/check', methods=["GET", "POST"])
def check():
    
    # クライアントから画像ゲット
    image1 = request.files["image1"]
    image2 = request.files["image2"]
    # メッサージュエラー
    messages = ""
    # 公的証明証ゲット
    type = str(request.form["type"])
    # 画像ファイルなし時にホームページ戻り
    if image1.filename == '' or image2.filename == '':
        return render_template("index.html")

    # サーバーに画像保存
    path1 = os.path.join(app.config['UPLOAD_FOLDER'], image1.filename)
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], image2.filename)
    image1.save(path1)
    image2.save(path2)
    
    client = vision.ImageAnnotatorClient()

    with io.open(path1, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    print("text", response)
    #texts = response.text_annotations[0].description
    
    if not response:
        os.remove(path1)
        os.remove(path2)

        resp = jsonify({'result':'カードをアップロードしてください。'})
        resp.status_code = 201
        return resp

    with io.open(path2, 'rb') as image_file:
        content2 = image_file.read()

    image2 = vision.Image(content=content2)

    response2 = client.text_detection(image=image2)
    
    #texts2 = response.text_annotations[0].description

    if(response2 != ""):
        os.remove(path1)
        os.remove(path2)

        resp = jsonify({'result':'文字をついていない写真をアップロードしてください。'})
        resp.status_code = 201
        return resp




    # 顔検出ー＞二つの画像の顔を比較して同じかどうか実行
    result_from_detect = detectImage(path1,path2)
    linear_val = (1.0 - result_from_detect[1]) / (0.8)
    accuracy ='{percent:.2%}'.format(percent=face_distance_to_conf(result_from_detect[1]))

    # "1":運転免許証
    # "2":パスポート
    # "3":マイナンバー
    # "4":在留カード 
    # "5":保険証 
    if(type == "1"): 
        # 運転免許証の情報ゲット
        messages =  getDriversLicense(path1)
    elif(type == "2"): 
        # パスポート情報ゲット
        messages =  getPassport(path1)
    elif(type == "3"):
        # マイナンバーゲット
        messages =  getMyNumber(path1) 
    elif(type == "4"): 
        # 在留カード
        messages =  getResidenceCard(path1) 
    elif(type == "5"): 
        # 保険証情報ゲット
        messages =  getInsuranceCatd(path1)
    if result_from_detect[2]:
        # 写真ぼやける時のエラー

        os.remove(path1)
        os.remove(path2)
        return render_template("index.html",message="写真がぼやけてしまいまして、もう一度やり直してください")
    else:
        if result_from_detect[0]:
            return render_template("index.html", result="一致する",accuracy="同じ : " + accuracy,path1 = path1,path2=path2,messages=messages)
        else:
            return render_template("index.html", result="一致しない",accuracy="同じ : " + accuracy,path1 = path1,path2=path2,messages=messages)
# 以下の画像拡張子許可
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
# 公的証明証タイプ
ALLOWED_TYPE= set(['1', '2', '3','4', '5'])

def allowed_file(filename):
    # 画像拡張子バリデーション
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/aws/api-recogntion/', methods=["GET", "POST"])
def recogntion():
    
    if 'image1' not in request.files:
        resp = jsonify({'result':'公的証明書が必要です。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    elif 'image2' not in request.files:
        resp = jsonify({'result':'顔写真が必要です。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp


    image1 = request.files["image1"]
    image2 = request.files["image2"]
    messages = ""


    if image1.filename == '':
        resp = jsonify({'result':'公的証明書が選択されていません。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    elif image2.filename == '':
        resp = jsonify({'result':'顔写真が選択されていません。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp

    
    if 'type' not in request.form:
        resp = jsonify({'result':'公的証明書書類が必要です。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    type = str(request.form["type"])
    if type not in ALLOWED_TYPE:
        resp = jsonify({'result':'公的証明書書類が選択されていません。'})
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    if (image1 and allowed_file(image1.filename)) and (image2 and allowed_file(image2.filename)):
        path1 = os.path.join(app.config['UPLOAD_FOLDER'], image1.filename)
        path2 = os.path.join(app.config['UPLOAD_FOLDER'], image2.filename)

        
        image1.save(path1)
        image2.save(path2)


        client = vision.ImageAnnotatorClient()

        with io.open(path1, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        print("text", response)
        #texts = response.text_annotations[0].description
        
        if not response:
            os.remove(path1)
            os.remove(path2)

            resp = jsonify({'result':'カードをアップロードしてください。'})
            resp.status_code = 201
            return resp

        with io.open(path2, 'rb') as image_file:
            content2 = image_file.read()

        image2 = vision.Image(content=content2)

        response2 = client.text_detection(image=image2)
        
        #texts2 = response.text_annotations[0].description

        if(response2 != ""):
            os.remove(path1)
            os.remove(path2)

            resp = jsonify({'result':'文字をついていない写真をアップロードしてください。'})
            resp.status_code = 201
            return resp


        result_from_detect = detectImage(path1,path2)
        linear_val = (1.0 - result_from_detect[1]) / (0.8)

        accuracy ='{percent:.2%}'.format(percent=face_distance_to_conf(result_from_detect[1]))
        # "1":運転免許証
        # "2":パスポート
        # "3":保険証 
        # "4":マイナンバー
        # "5":在留カード 
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

            resp = jsonify({'result':'写真がぼやけてしまいまして、もう一度やり直してください'})
            resp.status_code = 201
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp

        else:
            os.remove(path1)
            os.remove(path2)
            if result_from_detect[0]:
                resp = jsonify({'result':'一致ます','messages':messages})
                resp.status_code = 201
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp
            else:
                resp = jsonify({'result':'一致しません','messages':messages})
                resp.status_code = 201
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp

    else:
        resp = jsonify({'result' : '許可されるファイルタイプは png、jpg、jpegです。'})
        resp.status_code=400
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
	    

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

