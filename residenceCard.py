import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/var/www/html/recognition/text-recognition.json"

import cv2
import io
import xml.etree.ElementTree as ET


from google.cloud import vision
def getResidenceCard(image):
  #KCinput_file = "./document/在留カード（例）.png"

  # img = cv2.imread(input_file) # input_fileは画像のパス


  client = vision.ImageAnnotatorClient()
  with io.open(image, 'rb') as image_file:
      content = image_file.read()
  image = vision.Image(content=content)
  response = client.document_text_detection(image=image)




  tree = ET.parse("/var/www/html/recognition/configImg/residenceCard.xml") # input_xmlはxmlのパス
  root = tree.getroot()

  text_infos = []
  document = response.full_text_annotation
  for page in document.pages:
    for block in page.blocks:
      for paragraph in block.paragraphs:
        for word in paragraph.words:
          for symbol in word.symbols:
            bounding_box = symbol.bounding_box
            xmin = bounding_box.vertices[0].x
            ymin = bounding_box.vertices[0].y
            xmax = bounding_box.vertices[2].x
            ymax = bounding_box.vertices[2].y
            xcenter = (xmin+xmax)/2
            ycenter = (ymin+ymax)/2
            text = symbol.text
            text_infos.append([text, xcenter, ycenter])

  result_dict = {}
  for obj in root.findall("./object"):
    name = obj.find('name').text
    xmin = obj.find('bndbox').find('xmin').text
    ymin = obj.find('bndbox').find('ymin').text
    xmax = obj.find('bndbox').find('xmax').text
    ymax = obj.find('bndbox').find('ymax').text
    xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
    texts = ''
    for text_info in text_infos:
      text = text_info[0]
      xcenter = text_info[1]
      ycenter = text_info[2]
      if xmin <= xcenter <= xmax and ymin <= ycenter <= ymax:
        texts += text
    result_dict[name] = texts
  
  result_text = ""
  for k, v in result_dict.items():
    result_text += '{} : {}'.format(k, v)
  return result_text
