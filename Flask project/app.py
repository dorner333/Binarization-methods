# app-upload.py
import os

import matplotlib
import matplotlib.pyplot as plt
import skimage
import skimage.filters as skf
from skimage import io

from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = 'I have a dream'
window_size = 45

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'),
                                  FileRequired('File was empty!')])
    submit = SubmitField('Загрузить')


def methods_show(image):
    binary_otsu = image > skf.threshold_otsu(image)
    binary_niblack = image > skf.threshold_niblack(image, window_size=window_size, k=0.8)
    binary_sauvola = image > skf.threshold_sauvola(image, window_size=window_size)
    binary_isodata = image > skf.threshold_isodata(image)
    binary_tri = image > skf.threshold_triangle(image)

    bins = [image, binary_otsu, binary_niblack,
            binary_tri, binary_isodata, binary_sauvola]

    names = ['Original', 'Otsu', 'Niblack',
             'Triangle', 'Ridler-Calvard (isodata)', 'Sauvola']

    plt.figure(figsize=(24, 7))

    for i in range(len(bins)):
        plt.subplot(2, 3, i + 1)
        plt.imshow(bins[i], cmap=plt.cm.gray)
        plt.title(names[i])
        plt.axis('off')
    plt.savefig('uploads/img.jpg')


@app.route('/')
def home():
    return render_template('mainpage.html')


@app.route('/photos', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        img = io.imread(file_url, as_gray=True)
        methods_show(img)
        file_url = photos.url('img.jpg')
        # filename = photos.save(img)
        # file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('index.html', form=form, file_url=file_url)


@app.route('/examples')
def examples():
    return render_template('examples.html')


@app.route('/examples/scan')
def scan():
    img = io.imread('static/images/scan.jpg', as_gray=True)
    methods_show(img)
    file_url = photos.url('img.jpg')
    return render_template('scan.html', file_url=file_url)


@app.route('/examples/scan_bad')
def scan_bad():
    img = io.imread('static/images/scan_bad.jpg', as_gray=True)
    methods_show(img)
    file_url = photos.url('img.jpg')
    return render_template('scan_bad.html', file_url=file_url)


@app.route('/examples/cell')
def cell():
    img = io.imread('static/images/cell.png', as_gray=True)
    methods_show(img)
    file_url = photos.url('img.jpg')
    return render_template('cell.html', file_url=file_url)


@app.route('/examples/DIBCO')
def DIBCO():
    img = io.imread('static/images/DIBCO_2016.bmp', as_gray=True)
    methods_show(img)
    file_url = photos.url('img.jpg')
    return render_template('dibco.html', file_url=file_url)


if __name__ == '__main__':
    app.run(debug=True)
