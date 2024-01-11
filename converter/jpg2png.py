from PIL import Image
import os

if "output" not in os.listdir("."):
    os.mkdir("output")

for dir in os.listdir("converter/input"):
    if dir not in os.listdir("output"):
        os.mkdir("output/"+dir)
    
    for file in os.listdir("converter/input/"+dir):

        jpg_file = "converter/input/"+dir+"/"+file
        png_file = 'output/'+dir+"/"+file.split(".")[0]+".png"

        print(f"{jpg_file} -> {png_file}")

        Image.open(jpg_file).save(png_file, "PNG")