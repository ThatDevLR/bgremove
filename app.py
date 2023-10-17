# Import necessary libraries
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import os
from rembg import remove
from PIL import Image
import io

# Set up Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the route for background removal
@app.route('/', methods=['GET', 'POST'])
def remove_background_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename)
            file.save(file_path)

            # Use the rembg library to remove the background and make it transparent
            with open(file_path, 'rb') as input_file:
                input_data = input_file.read()

            with open(output_path, 'wb') as output_file:
                img = Image.open(io.BytesIO(input_data))
                img = remove(img, discard_threshold=1e-5, shift=1e-2)
                img = img.convert("RGBA")  # Convert the image to RGBA format to support transparency
                img.save(output_file, format='PNG')

            # Return the processed image to the user
            return send_file(output_path, as_attachment=True)

    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run()
