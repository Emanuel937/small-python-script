import runqrcode

# 1. Text or URL to turn into a QR code
data = input("Enter the text or URL to generate a QR code: ")

# 2. Create QR code instance
qr = runqrcode.QRCode(
    version=1,  # 1 to 40, controls the size of the QR code
    error_correction=runqrcode.constants.ERROR_CORRECT_H,  # high error correction
    box_size=10,  # size of each box in pixels
    border=4,     # thickness of the border
)
qr.add_data(data)  # add the data
qr.make(fit=True)  # fit the QR code size automatically

# 3. Create an image of the QR code
img = qr.make_image(fill_color="black", back_color="white")

# 4. Set the file name
filename = "qrcode.png"

# 5. Save the image as a PNG file
img.save(filename)

print(f"QR code generated and saved as '{filename}' ✅")
