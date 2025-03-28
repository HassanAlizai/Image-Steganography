# -*- coding: utf-8 -*-
"""Image-Steganography.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1chKAxD-JP5Ah7pbl6YSa1mtNV_ZsZQ9r
"""

from ipywidgets import (VBox, HBox, Tab, FileUpload, Dropdown, Button,
                        Output, Label, Layout, HTML)
from IPython.display import display, clear_output
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pyvirtualdisplay import Display

# Start virtual display
disp = Display(visible=0, size=(1280, 720))
disp.start()

# Custom styling
display(HTML("""
<style>
.widget-label { min-width: 180px !important; font-weight: bold; }
.preview-img { max-width: 100%; margin: 10px; border: 4px solid #007bff; border-radius: 12px; }
.button-style { background-color: #007bff; color: white; font-weight: bold; border-radius: 8px; padding: 10px; }
.status-box { border: 3px solid #007bff; padding: 15px; border-radius: 12px; background: #f8f9fa; font-size: 14px; }
.upload-box { border: 2px dashed #007bff; padding: 10px; border-radius: 10px; text-align: center; }
h1 { color: #2c3e50; text-align: center; font-size: 24px; }
</style>
"""))

# Widgets
upload_carrier = FileUpload(description="📂 Upload Carrier Image", multiple=False, layout=Layout(width='48%'))
upload_secret = FileUpload(description="📂 Upload Secret Image", multiple=False, layout=Layout(width='48%'))
bits_selector = Dropdown(options=[3, 4], value=4, description='LSB Bits:',
                         layout=Layout(width='30%'))
encode_btn = Button(description="🔒 Encode Image", button_style='success',
                    layout=Layout(width='200px'))
download_encoded = Button(description="⬇️ Download Encoded", disabled=True, layout=Layout(width='200px'))

upload_encoded = FileUpload(description="📂 Upload Encoded Image", multiple=False, layout=Layout(width='50%'))
decode_btn = Button(description="🔓 Decode Image", button_style='info', layout=Layout(width='200px'))
download_decoded = Button(description="⬇️ Download Decoded", disabled=True, layout=Layout(width='200px'))

preview_output = Output()
status_output = Output(layout=Layout(border='3px solid #007bff', padding='12px', border_radius='12px', background='#f8f9fa'))

def show_image(img, title):
    plt.figure(figsize=(7, 5))
    if len(img.shape) == 3:
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(img, cmap='gray')
    plt.title(title, fontsize=14)
    plt.axis('off')
    plt.show()

def process_encode(b):
    with status_output:
        clear_output()
        try:
            carrier = cv2.imdecode(np.frombuffer(next(iter(upload_carrier.value.values()))['content'], np.uint8), cv2.IMREAD_COLOR)
            secret = cv2.imdecode(np.frombuffer(next(iter(upload_secret.value.values()))['content'], np.uint8), cv2.IMREAD_COLOR)

            secret = cv2.resize(secret, (carrier.shape[1], carrier.shape[0]))
            bits = bits_selector.value
            mask = 0xFF ^ ((1 << bits) - 1)
            encoded = np.zeros_like(carrier)

            for c in range(3):
                encoded[:,:,c] = ((carrier[:,:,c] & mask) | (secret[:,:,c] >> (8 - bits)))

            global ENCODED_PATH
            ENCODED_PATH = '/content/encoded.png'
            cv2.imwrite(ENCODED_PATH, encoded)

            with preview_output:
                clear_output()
                print("🖼️ Encoded Image Preview:")
                show_image(encoded, "Encoded Image")

            download_encoded.disabled = False
            print("✅ Encoding successful! Secret embedded in the image.")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def process_decode(b):
    with status_output:
        clear_output()
        try:
            encoded = cv2.imdecode(np.frombuffer(next(iter(upload_encoded.value.values()))['content'], np.uint8), cv2.IMREAD_COLOR)
            bits = bits_selector.value
            mask = (1 << bits) - 1
            decoded = np.zeros_like(encoded)

            for c in range(3):
                decoded[:,:,c] = np.clip((encoded[:,:,c] & mask) << (8 - bits), 0, 255)

            global DECODED_PATH
            DECODED_PATH = '/content/decoded.png'
            cv2.imwrite(DECODED_PATH, decoded)

            with preview_output:
                clear_output()
                print("🕵️ Decoded Secret Preview:")
                show_image(decoded, "Revealed Secret")

            download_decoded.disabled = False
            print("🔎 Decoding successful! Hidden secret extracted.")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def download_file(path):
    from google.colab import files
    files.download(path)

# Connect buttons
encode_btn.on_click(process_encode)
decode_btn.on_click(process_decode)
download_encoded.on_click(lambda _: download_file(ENCODED_PATH))
download_decoded.on_click(lambda _: download_file(DECODED_PATH))

# Layout
encode_tab = VBox([
    Label("Select LSB Bits for Encoding:"),
    bits_selector,
    HBox([upload_carrier, upload_secret], layout=Layout(justify_content='center')),
    HBox([encode_btn, download_encoded], layout=Layout(justify_content='center')),
])

decode_tab = VBox([
    upload_encoded,
    HBox([decode_btn, download_decoded], layout=Layout(justify_content='center')),
])

tabs = Tab(children=[encode_tab, decode_tab])
tabs.set_title(0, "Encode")
tabs.set_title(1, "Decode")

display(VBox([
    HTML("<h1>🎨 Image Steganography Tool</h1>"),
    tabs,
    preview_output,
    status_output
]))