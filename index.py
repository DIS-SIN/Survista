from flask import (
    Blueprint, request, session, url_for, current_app, flash, g, render_template
)
from db import get_db
from auth import login_required 
from werkzeug.utils import secure_filename
from datetime import datetime
from celery_maker import make_celery
from utils.fileChecker import fileChecker
import os 
import hashlib
import zipfile
import shutil
import time
bp = Blueprint('index', __name__)
@bp.route('/', methods = ("GET","POST"))
@login_required
def index():
    get_db()
    db = g.index_db
    g.script_root = request.script_root
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
                    import api
                    api.run_check.delay()
                    api.run_check.delay()
                    api.run_check.delay()
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
@bp.route('/delete_resource', methods = ('POST',))
@login_required
def delete_resource():
    get_db()
    survey_id = request.form.get('id')
    query = "SELECT raw_data_path FROM index_table where id = {id}".format(
        id = survey_id
    )
    res = g.index_db.execute(query).fetchone()
    if res is None:
       return ('Resource has been already deleted', 503)
    else:
        os.chdir('./utils')
        raw_data_path = res['raw_data_path']
        raw_data_path = os.path.realpath(raw_data_path)
        os.chdir('../')
        shutil.rmtree(raw_data_path)
        import api
        api.run_check.delay()
    return ('',202)
@bp.route('/reprocess_resource', methods = ('POST',))
@login_required
def reprocess_resource():
    get_db()
    survey_id = request.form.get('id')
    query = "SELECT status_id, processed_data_path FROM index_table WHERE id = {id}".format(
        id = survey_id
    )
    res = g.index_db.execute(query).fetchone()
    if res is None:
       return ('Resource does not exist please refresh', 404)
    else:
        status = g.index_db.execute("SELECT status_name FROM statuses WHERE id = ?",(res['status_id'],)).fetchone()['status_name']
        if status == "processing":
            return ('Resource is already processing', 400)
        os.chdir('./utils')
        processed_data_path = res['processed_data_path']
        processed_data_path = os.path.realpath(processed_data_path)
        os.chdir('../')
        shutil.rmtree(processed_data_path)
        import api
        api.run_check.delay()
    return ('',202)