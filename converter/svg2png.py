import cairosvg
import os

if "output" not in os.listdir("."):
    os.mkdir("output")

for dir in os.listdir("converter/input"):
    if dir not in os.listdir("output"):
        os.mkdir("output/"+dir)
    
    for file in os.listdir("converter/input/"+dir):

        svg_file = "converter/input/"+dir+"/"+file
        png_file = 'output/'+dir+"/"+file.split(".")[0]+".png"

        print(f"{svg_file} -> {png_file}")

        cairosvg.svg2png(url=svg_file, write_to=png_file, output_width=320, output_height=320)