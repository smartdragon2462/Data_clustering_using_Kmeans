#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash, redirect, url_for
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import numpy as np
# import io
# import csv
# from werkzeug.utils import secure_filename
# from flask_sqlalchemy import SQLAlchemy
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from flask import jsonify
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
# app.config.from_object('config')
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
# db = SQLAlchemy(app)
# db.init_app(app)

# class Csv(db.Model):
#     __tablename__ = "csvs"
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String, nullable=False)
#
# db.create_all()
#
UPLOAD_FOLDER = 'static/csv'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}
#
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    global data
    global path_to_file
    global m_labels

    if request.method == 'POST':
        f = request.files['file']
        path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], '1.csv')
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], '1.csv'))
        # csvfile = Csv(filename=secure_filename(f.filename))
        # db.session.add(csv)
        # db.session.commit()
        data = pd.read_csv(path_to_file)
        head_data = np.array(data.head(10))
        m_size = np.shape(head_data)
        m_labels = list(data)

        #------------------------------------------------------
        m_str = '<div class="limiter"><div><div><div><table>'
        for m in range(len(m_labels)):
            if m == 0: m_str +='<thead><tr class="table100-head">'
            m_str += '<th class="columns">' +m_labels[m]+"</th>"
            if m == len(m_labels)-1: m_str +='</tr></thead>'

        # ------------------------------------------------------
        m_str+='<tbody>'
        for n in range(m_size[0]):
            for m in range(len(m_labels)):
                if m == 0: m_str += '<tr>'
                m_str += '<td class="columns">' +str( head_data[n][m] )+ "</td>"
                if m == len(m_labels) - 1: m_str += '</tr>'

        m_str +="</tbody></table></div></div></div></div>"

        # res = {}
    return m_str

# Error handlers.

@app.route('/result', methods=['POST'])
def get_result():
    global labels
    global data

    if request.method == 'POST':
        cluster_n = np.int16(request.values['cohorts'])
        le = LabelEncoder()
        m_str = ""
        if len(data)==0:
            return m_str

        data1 = pd.DataFrame.copy(data)
        categroy_ind = [2,4]
        for n in categroy_ind:
            m_category_name = m_labels[n]
            le.fit(data1[m_category_name].values)
            data1[m_category_name] = le.transform(data1[m_category_name].values)

        # Initializing KMeans
        kmeans = KMeans(n_clusters=cluster_n)

        # Fitting with inputs
        kmeans = kmeans.fit(data1)

        # Predicting the clusters
        labels = kmeans.predict(data1)

        # Getting the cluster centers
        C = kmeans.cluster_centers_

        # ------------------------------------------------------
        m_str = '<div class="limiter"><div><div><div><table>'
        for m in range(len(m_labels)):
            if m == 0:
                m_str += '<thead><tr class="table100-head"><th class="columns">Cohort</th>'

            m_str += '<th class="columns">' + m_labels[m] + "</th>"
            if m == len(m_labels) - 1: m_str += '</tr></thead>'

        # ------------------------------------------------------
        m_str += '<tbody>'
        json_string = '{'
        for n in range(len(C)):
            json_string +=  '"' + str(n) + '": [';
            for m in range(len(m_labels)):

                if m == 0:
                    m_str += '<tr data-toggle="modal" data-target="#myModal" class="cluster-row" id="' + str(n) + '" onclick="getCluster(' + str(n) + ')">'
                    m_str +='<td class="columns">' + str(n+1) + "</td>"
                    json_string += str(C[n][m])
                else:
                    json_string += ',' + str(C[n][m])

                m_str += '<td class="columns">' + str(np.round(C[n][m], 3)) + "</td>"
                if m == len(m_labels) - 1: m_str += '</tr>'

            if n == len(C) - 1:
                json_string += ']'
            else:
                json_string += '],'

        m_str += "</tbody></table></div></div></div></div>"
        json_string += '}'
        m_str += ";" + json_string

    return m_str

@app.route('/cluster', methods=['POST'])
def get_cluster():
    if request.method == 'POST':
        clusterID = np.int16(request.values['clusterID'])
        data2 =np.array(data[labels==clusterID])
        # ------------------------------------------------------
        m_str = '<div class="limiter"><div><div><div><table>'
        for m in range(len(m_labels)):
            if m == 0:
                m_str += '<thead><tr class="table100-head"><th class="columns">No</th>'

            m_str += '<th class="columns">' + m_labels[m] + "</th>"
            if m == len(m_labels) - 1: m_str += '</tr></thead>'

        # ------------------------------------------------------
        m_str += '<tbody>'
        for n in range(len(data2)):
            for m in range(len(m_labels)):
                if m == 0:
                    m_str += '<tr data-toggle="modal" data-target="#myModal" >'
                    m_str +='<td class="columns">' + str(n+1) + "</td>"
                if m==2 or m==4:
                    m_str += '<td class="columns">' + str(data2[n, m]) + "</td>"
                else:
                    m_str += '<td class="columns">' + str(np.round(data2[n, m], 3)) + "</td>"

                if m == len(m_labels) - 1: m_str += '</tr>'

        m_str += "</tbody></table></div></div></div></div>"

    return m_str

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return ""#render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return ""#render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='localhost', port=port)
    # app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
