from flask import (
    Blueprint, request, session, url_for, current_app, flash, g, render_template
)
from db import get_db
from auth import login_required 
from werkzeug.utils import secure_filename
from datetime import datetime
import os 
import hashlib
import zipfile
import shutil
import tasks
import time
bp = Blueprint('index', __name__)
@bp.route('/', methods = ("GET","POST"))
@login_required
def index():
    get_db()
    db = g.index_db
    if request.method == "POST":
        if 'survey_data' not in request.files:
            print(list(request.files.keys()))
            flash('No file was uploaded')
        else:
            file = request.files['survey_data']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                folder_hash = hashlib.sha256()
                folder_hash.update(bytes(g.user['username'],'utf-8'))
                folder_hash.update(bytes(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),'utf-8'))
                temp_folder_name = folder_hash.hexdigest()
                temp_folder_name = os.path.join(current_app.config['TEMP_PATH'], temp_folder_name)
                done = False
                count = 0 
                #in the impossible case that there is a hash collision
                while not done:
                    try:
                        os.mkdir(temp_folder_name)
                        done = True
                    except FileExistsError:
                        folder_hash.update(bytes(count))
                        temp_folder_name = folder_hash.hexdigest()
                        temp_folder_name = os.path.join(current_app.config['TEMP_PATH'], temp_folder_name)
                file_path = os.path.join(temp_folder_name, filename)
                file.save(file_path)
                myzip =  zipfile.ZipFile(file_path,'r') 
                inzip = myzip.namelist()
                f = 1
                error = False
                folder_name = None
                while f < len(inzip) and not error:
                    fname = inzip[f]
                    error = not allowed_inner_file(fname)
                    f += 1
                if error:
                    flash("zip file may only contain csv's")
                    myzip.close()
                    shutil.rmtree(temp_folder_name)
                elif request.form.get('name_change') is not None \
                     and request.form.get('name_change').strip(" ") != "" :
                    alt_name = request.form.get('name_change').strip(" ")
                    alt_name = secure_filename(alt_name)
                    alt_name = alt_name.split(".")[0]
                    count = 1
                    while os.path.isdir(os.path.join(current_app.static_folder,
                                        'raw_data',alt_name)):
                        alt_name += str(count)
                        count += 1
                    folder_name = alt_name
                if not error:
                    folder_in_zip = inzip[0].rstrip('/')
                    myzip.extractall(temp_folder_name)
                    myzip.close()
                    if folder_name is not None:
                        old_folder_path = os.path.join(temp_folder_name, folder_in_zip)
                        new_folder_path = os.path.join(temp_folder_name, folder_name)
                        os.rename(old_folder_path, new_folder_path) 
                        folder_in_zip = folder_name
                    else:
                        folder_name = folder_in_zip
                    count = 1
                    while os.path.isdir(os.path.join(current_app.static_folder,
                                        'raw_data',folder_name)):
                        folder_name = folder_in_zip + '_' + str(count)
                        count += 1
                    if count > 1:
                        print('count > 1')
                        new_folder_name = os.path.join(temp_folder_name, folder_name)
                        old_folder_name = os.path.join(temp_folder_name, folder_in_zip)
                        print(new_folder_name)
                        os.rename(old_folder_name, new_folder_name)
                        folder_name = new_folder_name
                    else:
                        folder_name = os.path.join(temp_folder_name, folder_name)
                    raw_data_path = os.path.join(current_app.static_folder,'raw_data')
                    shutil.move(folder_name, raw_data_path)
                    #TO-DO add workers config to specify how much workers should be started 
                    tasks.run_check.delay()
                    tasks.run_check.delay()
                    tasks.run_check.delay()
                    time.sleep(.3)
    query = "SELECT it.id, it.raw_data_path, it.processing_date, it.survey_name, st.status_name AS status FROM index_table AS it INNER JOIN statuses AS st ON it.status_id = st.id"
    g.surveys = db.execute(query).fetchall()
    temp = []
    if g.surveys is not None:
        for row in g.surveys:
            new_row = dict(row)
            new_row['filename'] = new_row['raw_data_path'].rsplit(os.path.sep,1)[1]
            temp.append(new_row)
        g.surveys = temp                
    return render_template('index/index.html')
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in  \
            current_app.config['ALLOWED_EXTENSIONS']
def allowed_inner_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] == "csv"
