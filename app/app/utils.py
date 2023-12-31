import os
import sys, json
from uuid import uuid4
import matplotlib
matplotlib.use("Agg")

from matplotlib.patches import Polygon

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.transforms as tfrms
import numpy as np
import os
import xmltodict
import rasterio
import shutil
import json
from haversine import haversine, Unit
import utm
from glob import glob
import zipfile
import imutils
from glob import glob
import cv2
import zipfile
import wget



"""
Pour tester ce module indépendamant décomment ce qui suit:

class MySetting:
  STATICFILES_DIR: os.path.curdir
  DATASETS_DIR: os.path.curdir

settings = MySetting()
"""



"""
Pour tester ce module indépendamant commentez la ligne

  from app.config import settings

"""
from app.config import settings


user = { 'user_name': '', 'password':'', 'plateform':'https://apihub.copernicus.eu/apihub'}
geomap = read_geojson(os.path.join(settings.STATICFILES_DIR, 'map.geojson'))

#(long,lat)
polygone = geomap["features"][0]["geometry"]["coordinates"][0]
# polygone = geomap["features"][0]["geometry"]["coordinates"]

name = "S2B_MSIL2A_20230104T103329_N0509_R108_T30NUM_20230104T132032.SAFE"
path = name+"/GRANULE/*/IMG_DATA/R10m"+"/*.jp2"

def get_absolute_path(filename):
  return os.path.join(settings.STATICFILES_DIR, filename)

def get_dataset_path(filename):
  return os.path.join(settings.DATASETS_DIR, filename)

def create_random_directory(root_dir: str) -> str:
    while True:
      filename = str(uuid4())
      path = os.path.join(root_dir, filename)
      if not os.path.exists(path):
        try:
          os.makedirs(path)
          return filename
        except:
          print(f"#### ERROR while creating {path} ")
      print("\n\n------------- find_available_filename ------------------------")

def get_random_filename(root_dir: str) -> str:
    while True:
      filename = str(uuid4())
      path = os.path.join(root_dir, filename)
      if not os.path.exists(path):
        return filename
      
x = glob(get_absolute_path(path))


def map_number(number):
  return str(0)+str(number) if len(str(number))==1 else str(number)

def unzip():
  files = glob('*.zip', root_dir=settings.DATASETS_DIR)
  for file in files:
    with zipfile.ZipFile(get_dataset_path(file), 'r') as zip_ref:
      zip_ref.extractall(settings.DATASETS_DIR)

def select_best_cloud_coverage_tile():
  tile_names = {}
  cld_prob = []
  folders = glob('*.SAFE', root_dir=settings.DATASETS_DIR)
  if len(folders) == 0:
    raise Exception(f"NO Tile found in DATASETS_DIR = {settings.DATASETS_DIR}")
  for fold in folders:
    metadata_path = fold+"/MTD_MSIL2A.xml"
    xml_file=open(os.path.join(settings.DATASETS_DIR, metadata_path),"r")
    xml_string=xml_file.read()
    python_dict=xmltodict.parse(xml_string)
    cld = float(python_dict["n1:Level-2A_User_Product"]["n1:Quality_Indicators_Info"]["Cloud_Coverage_Assessment"])
    tile_names[cld] = fold
    cld_prob.append(cld)
    name = tile_names[min(cld_prob)]
    dates = name.split('_')[2][:8]
    acquisition_date = datetime.strptime(dates, "%Y%m%d")
    today = datetime.now()
    delta = (today - acquisition_date)
    days_ago = delta.days
  return name,min(cld_prob),days_ago

#haversine distance calculation (lat,long)
def distance(ref,point,resolution=20):
  dist = round(haversine(ref, point, Unit.METERS)/resolution)
  return dist

def distance_cartesian(x1, y1, x2, y2,resolution=10):
  return int(np.sqrt(((x1-x2)**2+(y1-y2)**2))/resolution)

def coords_to_pixels(ref, utm, m=10):
    """ Convert UTM coordinates to pixel coordinates"""

    x = int((utm[0] - ref[0])/m)
    y = int((ref[1] - utm[1])/m)

    return x, y

def cartesion_distance(polygone):
  X = []
  Y = []
  for p in polygone:
    x,y,_,_ = utm.from_latlon(p[1],p[0])
    X.append(x)
    Y.append(y)

  return X,Y

def coords_to_pixelsv2(ref, X,Y, m=10):
    """ Convert UTM coordinates to pixel coordinates"""
    X2 = []
    Y2 = []
    for utm in zip(X,Y):
      x = int((utm[0] - ref[0])/m)
      y = int((ref[1] - utm[1])/m)
      X2.append(x)
      Y2.append(y)

    return X2,Y2

def trasnlate(X,Y,x_min,y_min):
  X3 = []
  Y3 = []
  for x,y in zip(X,Y):
    X3.append((x-x_min))
    Y3.append((y-y_min))
  return X3,Y3


def ndvi(polygone, tile_name):
  """
  polygone: (lon,lat) format
  tile_name: name of tile with the most low cloud coverage
  """

  # Extract rectangle that include the polygone (long,lat)
  #long
  long_min = min([long[0] for long in polygone])
  long_max = max([long[0] for long in polygone])
  #lat
  lat_min = min([long[1] for long in polygone])
  lat_max = max([long[1] for long in polygone])
  #Extract tile  coordonnates (lat,long)
  tile_path = tile_name+"/INSPIRE.xml"
  xml_file=open(os.path.join(settings.DATASETS_DIR, tile_path),"r")
  xml_string=xml_file.read()
  python_dict=xmltodict.parse(xml_string)
  tile_coordonnates = python_dict["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:abstract"]["gco:CharacterString"].split()

  # S2 tile coordonnates
  lat,lon = float(tile_coordonnates[0]),float(tile_coordonnates[1])
  tile_coordonnate = [lat,lon]

  refx, refy, _, _ = utm.from_latlon(tile_coordonnate[0], tile_coordonnate[1])
  ax,ay,_,_ = utm.from_latlon(lat_min,long_min)
  bx,by,_,_ = utm.from_latlon(lat_max,long_max)

  ref = [refx, refy]
  utm_min = [ax,ay]
  utm_max = [bx,by]
  x_min,y_max = coords_to_pixels(ref,utm_min)
  x_max,y_min = coords_to_pixels(ref,utm_max)

  # calculate the new polygon reprojected
  X,Y = cartesion_distance(polygone)
  X,Y = coords_to_pixelsv2(ref,X,Y)
  X,Y = trasnlate(X,Y,x_min,y_min)
  # read images
  path_4 = tile_name+"/GRANULE/*/IMG_DATA/R10m/*_B04_10m.jp2"
  path_8 = tile_name+"/GRANULE/*/IMG_DATA/R10m/*_B08_10m.jp2"

  red_object = rasterio.open(get_dataset_path(glob(path_4, root_dir=settings.DATASETS_DIR)[0]))
  nir_object = rasterio.open(get_dataset_path(glob(path_8, root_dir=settings.DATASETS_DIR)[0]))
  red = red_object.read()
  nir = nir_object.read()
  red,nir = red[0],nir[0]
  # extract area and remove unsigne
  sub_red = red[y_min:y_max+1,x_min:x_max+1].astype(np.float16)
  sub_nir = nir[y_min:y_max+1,x_min:x_max+1].astype(np.float16)

  # NDVI
  ndvi_image = ((sub_nir - sub_red)/(sub_nir+sub_red))
  ndvi_mean_value = ndvi_image.mean()
  # np.save("ndvit2.npy",ndvi_image)
  return ndvi_image,ndvi_mean_value,X,Y

def viz_data_ndvi(image,X,Y) -> str:
    colors = [(250/255,198/255,104/255), (0/255,110/255,51/255)] # ndvi colors
    polygon = Polygon([(u[0],u[1]) for u in zip(X,Y)],fc='none', ec='gold', lw=1)
    cm = LinearSegmentedColormap.from_list("Custom", colors, N=20)
    h,w = image.shape
    plt.imshow(image, cmap= cm)
    plt.colorbar()
    ax = plt.gca()
    ax.add_patch(polygon)
    #plt.plot(X,Y)
    filename = f"{str(datetime.now())}__ndvi__{uuid4()}.png"
    abs_path = get_absolute_path(filename)
    plt.savefig(abs_path)

    plt.clf()
    
    return abs_path


def delete_zips():
  files = glob('*.zip', root_dir=settings.DATASETS_DIR)
  for f in files:
    os.remove(get_dataset_path(f))

def superficie(image,X,Y):
    pts = np.array([[u[0],u[1]] for u in zip(X,Y)]) #,fc='none', ec='gold', lw=1
    ## (1) Crop the bounding rect
    rect = cv2.boundingRect(pts)
    x,y,w,h = rect
    croped = image[y:y+h, x:x+w].copy()
    ## (2) make mask
    pts = pts - pts.min(axis=0)
    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
    ## (3) do bit-op
    dst = cv2.bitwise_and(croped, croped, mask=mask)

    ## (4) add the white background
    bg = np.ones_like(croped, np.uint8)*255
    cv2.bitwise_not(bg,bg, mask=mask)
    dst2 = bg+ dst
    sup = sum(np.unique(mask,return_counts=True)[1][1:])*100
    # cv2.imwrite("croped.png", croped)
    # cv2.imwrite("mask.png", mask)
    return sup

import base64
from PIL import Image
from io import BytesIO
import pickle

def from_image_base64(image_path: str) -> str:
    image = Image.open(image_path)

    # Préparer un buffer en mémoire pour l'image
    buffered = BytesIO()

    # Enregistrer l'image dans le buffer en format PNG
    image.save(buffered, format="PNG")

    # Obtenir les données binaires de l'image
    img_data = buffered.getvalue()

    # Convertir les données binaires en chaîne base64
    img_base64 = base64.b64encode(img_data).decode()
    header = "data:image/jpeg;base64,"
    return header + img_base64

def from_matrix_to_base64(matrix) -> str:
    matrice_serialisee = pickle.dumps(matrix)

    img_base64 = base64.b64encode(matrice_serialisee).decode()

    return img_base64

def from_base64_to_matrix(base64_string: str):
  donnees_binaires = base64.b64decode(base64_string)
  matrice_numpy = pickle.loads(donnees_binaires)
  return matrice_numpy

from app import schemas

def pipeline_ndvi(polygone: list[list]) -> schemas.processing_request.ProcessingOutput:
  """
  polygone : coordinate of area draw on the map
  """
  print("========> Download termined")
  unzip()
  print("========> Unzip termined")
  print("========> Selection of best tile")
  tile_name, prob, days_ago = select_best_cloud_coverage_tile()
  print("========> Best tile selected")

  #print(tile_name)

  print("========> Computing ndvi")
  image_ndvi, value_ndvi, X, Y = ndvi(polygone,tile_name)

  print("========> Computing area surface")
  superifcie_polygone = superficie(image_ndvi,X,Y)
  print("========> Saving file")
  imagepath = viz_data_ndvi(image_ndvi,X,Y)
  
  print("========> Converting to base64")
  image_base64 = from_image_base64(imagepath)

  print("========> Removing useless files")
  delete_zips()
  os.remove(imagepath)

  print("========> Process completed")
  matrix = image_ndvi.tolist()

  print(image_ndvi)

  return schemas.processing_request.ProcessingOutput(
    matrix=matrix,
    image_base64=image_base64,
    mean_value=value_ndvi, 
    polygon_area=superifcie_polygone,
    used_tile_name = tile_name
  )

# def pipeline_ndvi_evolution(last: np.ndarray, new: np.ndarray) -> (str, str):
#   # last = np.array(scene1)
#   # new = np.array(scene2)
  
#   diff = (new-last)
#   y1 = last.flatten()
#   y2 = new.flatten()
#   y3 = diff.flatten()
#   x= [i for i in range(len(y1))]       
#   plt.figure(figsize=(10,4))

#   #scene T1
#   plt.plot(x,y1,c='red',label="ndvi T1")
#   #scene T2
#   print("2 plot")
#   plt.plot(x,y2,label="ndvi T2",c='green')
#   # diff
#   # plt.plot(x,y3,label="ndvi diff",c='k')
#   plt.title('Evolution du NDVI au niveau du pixel')
#   plt.xlabel(f'Pixels ({len(x)} valeurs)', fontsize=14,)
#   plt.ylabel('NDVI', fontsize=14)
#   plt.legend()
#   plt.xticks(np.arange(min(x), max(x)+1, 20))

#   filename = f"{str(datetime.now())}__evo_ndvi__{uuid4()}.png"
#   abs_path = get_absolute_path(filename)
#   plt.savefig(abs_path)
#   plt.clf()

#   result_base64 = from_image_base64(abs_path)

#   return abs_path, result_base64
  
def pipeline_ndvi_evolution(last: np.ndarray, new: np.ndarray) -> (str, str):
  # last = np.array(scene1)
  # new = np.array(scene2)
  
  diff = (new-last)
  y1 = last.flatten()
  y2 = new.flatten()
  y3 = diff.flatten()

  x= [i for i in range(len(y1))]

  # Nombre de points de données
  nombre_points = len(y1)

  # Largeur de base pour 1000 points de données
  largeur_base = 10  # 10 pouces pour 1000 points de données

  # Calculer la nouvelle largeur proportionnelle au nombre de points
  largeur_fig = largeur_base * (nombre_points / 1000)
  largeur_fig = max(min(largeur_fig, 100), largeur_base) 
  largeur_fig = min(largeur_fig, 65500)
  plt.figure(figsize=(largeur_fig, largeur_fig * 0.4))

  #scene T1
  plt.plot(x,y1 ,c='red',label="ndvi T1")
  #scene T2
  print("2 plot")
  plt.plot(x, y2,label="ndvi T2",c='green')
  # diff
  # plt.plot(x,y3,label="ndvi diff",c='k')
  plt.title('Evolution du NDVI au niveau du pixel')
  plt.xlabel(f'Pixels ({len(x)} valeurs sur {len(x)})', fontsize=14,)
  plt.ylabel('NDVI', fontsize=14)
  plt.legend()
  plt.xticks(np.arange(min(x), max(x)+1, 20))

  filename = f"{str(datetime.now())}__evo_ndvi__{uuid4()}.png"
  abs_path = get_absolute_path(filename)
  plt.savefig(abs_path)
  plt.clf()

  result_base64 = from_image_base64(abs_path)

  return result_base64
  

########################################### NDMI ########################################################
############################################
############################################

def viz_data_ndmi(image,X,Y, working_dir: str):
    colors = [(165/255, 38/255, 10/255),(119/255, 181/255, 254/255)] # ndvi colors
    polygon = Polygon([(u[0],u[1]) for u in zip(X,Y)],fc='none', ec='gold', lw=1)
    cm = LinearSegmentedColormap.from_list("Custom", colors, N=20)
    h,w = image.shape
    im = plt.imshow(image, cmap= cm)
    plt.colorbar()
    ax = plt.gca()
    ax.add_patch(polygon)
    #plt.plot(X,Y)
    filename = f"{str(datetime.now())}__ndmi__{uuid4()}.png"
    abs_path = os.path.join(working_dir, filename)
    plt.savefig(abs_path)

    plt.clf()
    return abs_path


from osgeo import gdal
def ndmi(polygone, tile_name):

  # Extract rectangle that include the polygone (long,lat)
  #long
  long_min = min([long[0] for long in polygone])
  long_max = max([long[0] for long in polygone])
  #lat
  lat_min = min([long[1] for long in polygone])
  lat_max = max([long[1] for long in polygone])

  #Extract tile  coordonnates (lat,long)
  tile_path = tile_name+"/INSPIRE.xml"
  xml_file=open(get_dataset_path(tile_path),"r")
  xml_string=xml_file.read()
  python_dict=xmltodict.parse(xml_string)
  tile_coordonnates = python_dict["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:abstract"]["gco:CharacterString"].split()

  # S2 tile coordonnates
  lat,lon = float(tile_coordonnates[0]),float(tile_coordonnates[1])
  tile_coordonnate = [lat,lon]

  refx, refy, _, _ = utm.from_latlon(tile_coordonnate[0], tile_coordonnate[1])
  ax,ay,_,_ = utm.from_latlon(lat_min,long_min)
  bx,by,_,_ = utm.from_latlon(lat_max,long_max)

  ref = [refx, refy]
  utm_min = [ax,ay]
  utm_max = [bx,by]
  x_min,y_max = coords_to_pixels(ref,utm_min)
  x_max,y_min = coords_to_pixels(ref,utm_max)

  # calculate the new polygon reprojected
  X,Y = cartesion_distance(polygone)
  X,Y = coords_to_pixelsv2(ref,X,Y)
  X,Y = trasnlate(X,Y,x_min,y_min)
  # read images
  path_8 = tile_name+"/GRANULE/*/IMG_DATA/R10m/*_B08_10m.jp2"
  path_11 = tile_name+"/GRANULE/*/IMG_DATA/R20m/*_B11_20m.jp2"

  nir_object = gdal.Open(get_dataset_path(glob(path_8, root_dir=settings.DATASETS_DIR)[0]))
  rb = nir_object.GetRasterBand(1)
  nir = rb.ReadAsArray()
  
  name_b11 = f"ndmi__{str(datetime.now())}__{get_random_filename(settings.STATICFILES_DIR)}.tif" # os.path.join(working_dir, "ndmi_resample.tif")
  path_11 = get_dataset_path(glob(path_11, root_dir=settings.DATASETS_DIR)[0])

  dst = gdal.Translate(name_b11, path_11, width=10980, height=10980,resampleAlg ="nearest")
  rbs = dst.GetRasterBand(1)
  b11 = rbs.ReadAsArray()
  
  # extract area and remove unsigne
  sub_b11 = b11[y_min:y_max+1,x_min:x_max+1].astype(np.float16)
  sub_nir = nir[y_min:y_max+1,x_min:x_max+1].astype(np.float16)

  # NDMI
  ndmi_image = ((sub_nir - sub_b11)/(sub_nir+sub_b11))
  ndmi_mean_value = ndmi_image.mean()
  return ndmi_image,ndmi_mean_value,X,Y

# pipeline
def pipeline_ndmi(polygone: list[list]):
  print("========> Download termined")
  unzip()
  print("========> Unzip termined")
  tile_name,prob,days_ago = select_best_cloud_coverage_tile()
  print("========> Best tile selection termined")

  image_ndmi,value_ndmi,X,Y= ndmi(polygone,tile_name)
  print("========> NDMI calculation termined")
  
  superifcie_polygone = superficie(image_ndmi,X,Y)
  
  print("========> Saving VIZ")
  imagepath = viz_data_ndmi(image_ndmi,X,Y, working_dir = settings.STATICFILES_DIR)
  
  print("========> Converting to base64")
  image_base64 = from_image_base64(imagepath)
  print("========> VIZ termined")

  print("========> Removing useless files")
  delete_zips()
  os.remove(imagepath)
  print("========> files sources deteleted")

  print("========> Process completed")
  matrix = image_ndmi.tolist()

  return schemas.processing_request.ProcessingOutput(
    matrix=matrix,
    image_base64=image_base64,
    mean_value=value_ndmi, 
    polygon_area=superifcie_polygone,
    used_tile_name = tile_name
  )
