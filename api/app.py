#importing libraries
from extract_txt import read_files
from txt_processing import preprocess
from txt_to_features import txt_features, feats_reduce
from extract_entities import get_number, get_email, rm_email, rm_number, get_name, get_skills
from model import simil
import pandas as pd
import json
import os
import uuid
import datetime
from flask import Flask, abort, flash, request, redirect, url_for, render_template, send_file
import plotly.express as px
from gpt import gptProcess


#used directories for data, downloading and uploading files 
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files\\resumes\\')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files\\outputs\\')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files\\processed\\')
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data\\')

# Make directory if UPLOAD_FOLDER does not exist
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Make directory if DOWNLOAD_FOLDER does not exist
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)
#Flask app config 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['SECRET_KEY'] = 'nani?!'

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])








def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
 
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    app.logger.info(request.files)
    upload_files = request.files.getlist('file')
    app.logger.info(upload_files)
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not upload_files:
        flash('No selected file')
        return redirect(request.url)
    for file in upload_files:
        original_filename = file.filename
        if allowed_file(original_filename):
            extension = original_filename.rsplit('.', 1)[1].lower()
            filename = str(uuid.uuid1()) + '.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
            files = _get_files()
            files[filename] = original_filename
            with open(file_list, 'w') as fh:
                json.dump(files, fh)
 
    flash('Upload succeeded')
    return redirect(url_for('upload_file'))

 
@app.route('/download/<code>', methods=['GET'])
def download(code):
    files = _get_files()
    if code in files:
        path = os.path.join(UPLOAD_FOLDER, code)
        if os.path.exists(path):
            return send_file(path, as_attachment=False)
    abort(404)
 

@app.route('/view_result/<file>', methods=['GET'])
def view_result(file):
    filepath = os.path.join(DOWNLOAD_FOLDER, file)
    print(filepath)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        # fig = px.sunburst(df, email='E-Mail ID', matching='JD 1', phoneNumber='Phone No.')
        fig = px.sunburst(df, path=['E-Mail', 'Skills'], values='JD 1')
        return fig.to_html()
        # return send_file(filepath, as_attachment=False)
    abort(404)


def _show_page():
    files = _get_files()
    return render_template('index.html', files=files)
 
def _get_files():
    file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
    if os.path.exists(file_list):
        with open(file_list) as fh:
            return json.load(fh)
    return {}

@app.route('/', methods=['GET'])
def main_page():
    return _show_page()

@app.route('/result', methods = ["GET"])
def result():
    file_list = os.listdir(DOWNLOAD_FOLDER)
    # for file in file_list:
    #     file = os.path.join(DOWNLOAD_FOLDER, file)
    #     if os.path.exists(file):
    #         with open(file) as fr:
    #             print(fr)
    files_send = {index: file for index, file in enumerate(file_list)}

    return render_template('result.html', files=files_send)

@app.route('/process',methods=["POST"])
def process():
    if request.method == 'POST':

        rawtext = request.form['rawtext']
        jdtxt=[rawtext]
        resumetxt=read_files(UPLOAD_FOLDER)
        p_resumetxt = preprocess(resumetxt)
        # p_resumetxt = resumetxt
        p_jdtxt = preprocess(jdtxt)

        feats = txt_features(p_resumetxt, p_jdtxt)
        feats_red = feats_reduce(feats)

        df = simil(feats_red, p_resumetxt, p_jdtxt)

        t = pd.DataFrame({'Original Resume':resumetxt, 'Processed Resume':p_resumetxt})
        dt = pd.concat([df,t],axis=1)

        # dt['Phone No.']=dt['Processed Resume'].apply(lambda x: get_number(x))
        
        # dt['E-Mail ID']=dt['Original Resume'].apply(lambda x: get_email(x))

        # dt['Original']=dt['Original Resume'].apply(lambda x: rm_number(x))
        # dt['Original']=dt['Original'].apply(lambda x: rm_email(x))
        # dt['Candidate\'s Name']=dt['Original'].apply(lambda x: get_name(x))

        # gptProcess(dt['Original Resume'])

        # skills = pd.read_csv(DATA_FOLDER+'skill_red.csv')
        # skills = skills.values.flatten().tolist()
        # skill = []
        # for z in skills:
        #     r = z.lower()
        #     skill.append(r)

        # dt['Skills']=dt['Processed Resume'].apply(lambda x: get_skills(x,skill))
        # dt = dt.drop(columns=['Original','Original Resume', 'Processed Resume'])
        datetimenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        processed_path = OUTPUT_FOLDER + "Candidates-" + datetimenow
        os.makedirs(processed_path)
        sorted_dt = dt.sort_values(by=['JD 1'], ascending=False)
        sorted_dt = sorted_dt.head(3)
        sorted_dt['Gpt-Form'] = sorted_dt.apply(lambda x: gptProcess(x['Original Resume'], processed_path, x.name), axis = 1)
        sorted_dt = sorted_dt.drop(columns=['Original Resume', 'Processed Resume'])
        # sorted_dt['Phone']=sorted_dt['Gpt-Form'].apply(lambda x: get_number(x))
        sorted_dt['E-Mail']=sorted_dt['Gpt-Form'].apply(lambda x: get_email(x))
        # sorted_dt['Name']=sorted_dt['Gpt-Form'].apply(lambda x: get_name(x))

        skills = pd.read_csv(DATA_FOLDER+'skill_red.csv')
        skills = skills.values.flatten().tolist()
        skill = []
        for z in skills:
            r = z.lower()
            skill.append(r)

        sorted_dt['Skills']=sorted_dt['Gpt-Form'].apply(lambda x: get_skills(x,skill))
        
        out_path = DOWNLOAD_FOLDER+"Candidates-" + datetimenow + ".csv"
        print(sorted_dt)
        sorted_dt.to_csv(out_path, index=False)
        send_file(out_path, as_attachment=True)
        return redirect(url_for('result'))

if __name__=="__main__":
    app.run(port=8080, debug=False)
