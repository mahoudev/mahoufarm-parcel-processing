from PIL import Image
import numpy as np
from app.config import settings
import os
from app.utils import *

# Chemin vers votre image
# img1 = os.path.join(settings.STATICFILES_DIR, "ndvi__2023-11-29 16:28:20.703555__5839dd14-5425-48a6-adb7-2405eb30f25b.png")
# img2 = os.path.join(settings.STATICFILES_DIR, "ndvi__2023-11-29 16:31:46.462994__973c29f3-470b-4ab4-9108-68d27ee48528.png")
str1 = ""
with open("img.txt") as fp:
    str1 = fp.read()

matrice = np.array([[1, 2, 3], [4, 5, 6]])
content = from_matrix_to_base64(matrice)
print(content[:15])
my_array = from_base64_to_matrix(content)
print(type(my_array))
# img2 = from_base64_to_matrix(str1)
# ndvi_evolution(
#     Image.open(img1), 
#     Image.open(img2)
# )

##

"""
import numpy as np
from PIL import Image
import io
import base64

from app.utils import *

# Exemple de matrice NumPy (remplacez ceci par votre matrice)
matrice = np.random.rand(162, 232) # Matrice d'une image 100x100
matrice = matrice.astype(np.float16)
print("\n\n\n RECIEVED IMAHE ARRAY ", matrice, " \n\n OF TYPE ",  type(matrice))

# Convertir la matrice en image
image = Image.fromarray(matrice)

# Enregistrer l'image dans un buffer de mémoire
buffer = io.BytesIO()
image.save(buffer, format="PNG")
buffer.seek(0)

# Encoder le contenu du buffer en base64
data_base64 = base64.b64encode(buffer.getvalue()).decode()
data_base64 =from_image_matrix_to_base64(matrice)


# polygon = [
#             [
#               -4.070148337954436,
#               5.428984937975557
#             ],
#             [
#               -4.070148337954436,
#               5.414361926634001
#             ],
#             [
#               -4.049325860500318,
#               5.414361926634001
#             ],
#             [
#               -4.049325860500318,
#               5.428984937975557
#             ],
#             [
#               -4.070148337954436,
#               5.428984937975557
#             ]
#           ]

# pipeline_ndvi(polygon)
# print(data_base64[:15])
"""