#apps/utils/adminhandle_helper.py
import os
from werkzeug.utils import secure_filename
from PIL import Image

from flask import flash, get_flashed_messages, redirect, render_template_string, request, send_from_directory, url_for

def af_allowed_file2(filename="flangelist2003.mdb", allowedextensions={'mdb'}):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedextensions

def af_ifpathnotexist(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def af_downloadfile(folder="static", name="flangelist2003.mdb"):
    af_ifpathnotexist(folder)
    try:
        return send_from_directory(folder, name, as_attachment=True)
    except FileNotFoundError:
        return 'File not found', 404
    
def af_uploadfile(redirectlink="flangehandle.flangehandle", folder="static", name="flangelist2003.mdb", allowedextensions={'mdb'}):
    
    af_ifpathnotexist(folder)

    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file'] #<...name="file">
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for(redirectlink))
    
    if file and af_allowed_file2(file.filename, allowedextensions):
        filename = name  # Enforce the filename to be "flange.mdb"
        file.save(os.path.join(folder, filename))
        flash('File successfully uploaded')
        return redirect(url_for(redirectlink))
    
    return 'File not allowed', 400

def af_htmlhandletemplate(linkdownload="/flangehandle/download", linkupload="/flangehandle/upload", linkimages="/flangehandle/images", name="flange.mdb", linkback="/flangehandle"):
    html = ""
    html += """
        <!doctype html>
        <html>

            <head>
                <title>Upload/Download File</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="{{ url_for('static', filename='bootstrap.min.css') }}" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
                <style>
                    body {
                        background-color: aliceblue;
                        background-image: url("{{ url_for('static', filename='images/flange.png') }}");
                        background-repeat: no-repeat;
                    }
                    .selectorDIV {
                        max-width: 800px;
                        margin: auto;
                        background-color: rgb(249, 252, 255);
                        margin-top: 20px;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        text-align: center;
                    }
                    .chooseDIV div {
                        background-color: #fff;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        width: 50%;
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        padding:10px;
                        margin:5px;
                    }
                    .chooseDIV div form input {
                        margin-bottom: 10px;
                    }
                </style>
            </head>

            <body>
                <div class="selectorDIV" style="
                        font-size: 40px;
                        padding: 5px;
                        margin: 10px;
                        margin-left: 20px;
                        position: absolute;
                    ">
                    <a href=\""""+linkback+"""\" style="
                        text-decoration: none;
                    " >🔙</a>
                </div>
                <div class="container selectorDIV">
                    <div class="d-flex justify-content-center chooseDIV">
                        <div>
                            <h1>📩Download File</h1>
                            <div class="form-control">
                                <a href=\""""+linkdownload+"""\">Download """+name+"""</a>
                            </div>
                        </div>
                        <div>
                            <h1>⬆️Upload File</h1>
                            <form action=\""""+linkupload+"""\" method="post" enctype="multipart/form-data">
                                <input type="file" name="file" class="form-control">
                                <input type="submit" value="Upload" class="btn btn-warning">
                            </form>
                        </div>
                    </div>"""

    html += af_render_flashed_messages()
    
    if linkimages != "":
        html += """
                <div class="d-flex justify-content-center align-items-center my-4">
                    <a href=\""""+linkimages+"""\">
                        <div class="form-control text-center">
                            Images
                        </div>
                    </a>
                </div>
                """
    html += """
            </body>

        </html>
    """
    return render_template_string(html)

def af_htmlhandletemplate2(linkdownload="/flangehandle/download", linkupload="/flangehandle/upload", linkimages="/flangehandle/images", name="flange.mdb", linkback="/flangehandle"):
    html = ""
    html += """
        <!doctype html>
        <html>

            <head>
                <title>Upload/Download File</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="{{ url_for('static', filename='bootstrap.min.css') }}" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
                <style>
                    body {
                        background-color: aliceblue;
                        background-image: url("{{ url_for('static', filename='images/flange.png') }}");
                        background-repeat: no-repeat;
                    }
                    .selectorDIV {
                        max-width: 800px;
                        margin: auto;
                        background-color: rgb(249, 252, 255);
                        margin-top: 20px;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        text-align: center;
                    }
                    .chooseDIV div {
                        background-color: #fff;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        width: 50%;
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        padding:10px;
                        margin:5px;
                    }
                    .chooseDIV div form input {
                        margin-bottom: 10px;
                    }
                </style>
            </head>

            <body>
                <div class="selectorDIV" style="
                        font-size: 40px;
                        padding: 5px;
                        margin: 10px;
                        margin-left: 20px;
                        position: absolute;
                    ">
                    <a href=\""""+linkback+"""\" style="
                        text-decoration: none;
                    " >🔙</a>
                </div>
                <div class="container selectorDIV">
                    <div class="d-flex justify-content-center chooseDIV">
                        <div>
                            <h1>📩Download File</h1>
                            <div class="form-control">
                                <a href=\""""+linkdownload+"""\">Download """+name+"""</a>
                            </div>
                        </div>
                        <div>
                            <h1>⬆️Upload File</h1>
                            <form action=\""""+linkupload+"""\" method="post" enctype="multipart/form-data">
                                <input type="file" name="file" class="form-control">
                                <input type="submit" value="Upload" class="btn btn-warning">
                            </form>
                        </div>
                    </div>"""

    html += af_render_flashed_messages()
    
    if linkimages != "":
        html += """
                <div class="d-flex justify-content-center align-items-center my-4">
                    <a href=\""""+linkimages+"""\">
                        <div class="form-control text-center">
                            Images
                        </div>
                    </a>
                </div>
                """
    html += """
            </body>

        </html>
    """
    return html


def af_render_flashed_messages():
    # Assume get_flashed_messages is defined and returns a list of messages
    messages = get_flashed_messages()
    if not messages:
        return ""

    # Start building the HTML string
    html = "<div class='flashed-messages'><br/><ul>"
    
    # Add each message as a list item
    for message in messages:
        html += f"<li>{message}</li>"
    
    # Close the unordered list and the div
    html += "</ul></div>"
    
    return html

def af_htmlimagehandletemplate(image_dir="static/images/flanges", linkrename="/flangehandle/images/rename", linkadd="/flangehandle/images/add"):

    # Path to the directory containing images
    # image_dir = os.path.join('static', 'images', 'flanges')

    # List all image files in the directory
    images = [
        {'name': file_name, 'src': f'/{image_dir}/{file_name}'}
        for file_name in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, file_name))
    ]

    html = """
        <!doctype html>
        <html>

        <head>
            <title>Upload/Download File</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="{{ url_for('static', filename='bootstrap.min.css') }}" rel="stylesheet"
                integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
            <style>
                body {
                    background-color: aliceblue;
                    background-image: url("{{ url_for('static', filename='images/flange.png') }}");
                    background-repeat: no-repeat;
                }

                .selectorDIV {
                    max-width: 800px;
                    margin: auto;
                    background-color: rgb(249, 252, 255);
                    margin-top: 20px;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }

                .chooseDIV div {
                    background-color: #fff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    width: 50%;
                    text-align: center;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 10px;
                    margin: 5px;
                }

                .chooseDIV div form input {
                    margin-bottom: 10px;
                }

                .title {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }

                .title h1 {
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    background-color: rgba(255, 255, 255, 0.9);
                    /* border-radius: 12px; */
                    width: fit-content;
                    padding: 0.5rem;
                }
            </style>
        </head>

        <body class="container my-3" style="position: relative;">
            <div class="title my-4">
                <h1 class="text-center">
                    Images
                </h1>
            </div>
            <a style="position: absolute;
            right: 10px;
            top: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            background-color: lightblue;
            font-weight: bold;
            padding: 10px;
            color: black;
            text-decoration: none;" href=\""""+linkadd+"""\">
                <div>
                    + Add image
                </div>
            </a>

            <div class="row">
                {% for im in images %}
                <div class="col-sm-6 col-md-4 col-lg-3 mb-4">
                    <div class="card"><img src="{{ im.src }}" class="card-img-top" alt="{{ im.name }}">
                        <div class="card-body text-center">
                            <h5 class="card-title">{{ im.name }}</h5><!-- Form for renaming the image -->
                            <form action=\""""+linkrename+"""\" method="post"><input type="hidden" name="old_name"
                                    value="{{ im.name }}"><input type="text" name="new_name" placeholder="New name"><button
                                    type="submit">Rename</button></form>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </body>

        </html>
    """

    return render_template_string(html, images=images)

def af_htmlimagehandletemplateadd(endpointupload="/flangehandle/images/upload", endpointback="/flangehandle/images"):
    html = """
<!doctype html>
<html>

<head>
    <title>Upload/Download File</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="{{ url_for('static', filename='bootstrap.min.css') }}" rel="stylesheet"
        integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
    <style>
        body {
            background-color: aliceblue;
            background-image: url("{{ url_for('static', filename='images/flange.png') }}");
            background-repeat: no-repeat;
        }

        .selectorDIV {
            max-width: 800px;
            margin: auto;
            background-color: rgb(249, 252, 255);
            margin-top: 20px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .chooseDIV div {
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 50%;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 10px;
            margin: 5px;
        }

        .chooseDIV div form input {
            margin-bottom: 10px;
        }

        .title {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .title h1 {
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            background-color: rgba(255, 255, 255, 0.9);
            /* border-radius: 12px; */
            width: fit-content;
            padding: 0.5rem;
        }
    </style>
</head>

<body class="container my-3" style="position: relative;">
    <div class="title my-4">
        <h1 class="text-center">
            Add Images
        </h1>
    </div>
    <a style="position: absolute;
    right: 10px;
    top: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    background-color: lightblue;
    font-weight: bold;
    padding: 10px;
    color: black;
    text-decoration: none;" href=\""""+endpointback+"""\">
        <div>
            Back
        </div>
    </a>

    <form style="max-width: 500px;" class="container w-50" action=\""""+endpointupload+"""\" method="post" enctype="multipart/form-data">
        <div class="row justify-content-center align-items-center my-4">
            <div class="w-50 mb-2">
                <input type="text" name="codename" class="form-control" placeholder="codename"
                    style="text-transform:uppercase;" required />
            </div>
            <div class="w-75 mb-2">
                <input type="file" name="image" accept="image/*" class="form-control" required />
            </div>
            <!-- <div class="d-flex justify-content-center align-items-center mb-2">
                <button class="btn btn-primary">
                    Upload
                </button>
            </div> -->
        </div>
        <div class="my-4 text-center">
            <button type="submit" class="form-control btn btn-warning w-50" value="Submit">
                Submit
            </button>
        </div>
    </form>
</body>

</html>
"""
    return render_template_string(html)

def af_htmlimagehandletemplateupload(image_dir="/static/images/flanges", allowed_extensions={'jpeg','png','jpg'}, redirectlink="/flangehandle/images"):
    # Directory to save uploaded images
    # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images', 'flanges')
    # UPLOAD_FOLDER = image_dir
    UPLOAD_FOLDER = os.path.join(os.getcwd()) + image_dir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Allowed file extensions
    # ALLOWED_EXTENSIONS = {'jpeg','png','jpg'}
    ALLOWED_EXTENSIONS = allowed_extensions

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        codename = request.form['codename'].upper()
        file = request.files['image']

        if file and allowed_file(file.filename):
            # Use secure_filename to safely handle user input filenames
            filename = secure_filename(f"{codename}.jpeg")
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Save the uploaded file
            file.save(filepath)

            # (Optional) Convert to JPEG in case it's not, use PIL
            with Image.open(filepath) as img:
                # if img.format != 'JPEG':
                #     img = img.convert('RGB')  # Convert to RGB mode if needed
                #     img.save(filepath, 'JPEG')
                
                img = img.convert('RGB')  # Convert to RGB mode if needed
                img.save(filepath, 'JPEG')

            # return redirect(url_for('upload_file'))

    return redirect(redirectlink)

def af_htmlimagehandletemplaterename(image_dir="static/images/flanges", redirectlink="/flangehandle/images"):
    old_name = request.form['old_name']
    new_name = request.form['new_name']

    # Ensure the old file exists and new file doesn't
    old_path = image_dir + "/" + old_name
    new_path = image_dir + "/" + new_name


    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        # Update the image list accordingly if needed
    else:
        # Handle error (e.g., file not found or new file name already used)
        pass

    return redirect(redirectlink)