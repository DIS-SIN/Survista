import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import string
from datetime import datetime 
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db 
import copy
bp = Blueprint('auth', __name__, url_prefix='/auth')
def login_required(view):
    @functools.wraps(view)
    def check_login_and_access(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        else:
            if g.user_status == 'deactivated':
                return redirect(url_for('auth.not_authorized'))
            return view(**kwargs)
    return check_login_and_access
@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == "POST":
        db, _ = get_db()
        username = request.form['username']
        password = request.form['password']
        error = None 
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        else:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            if user is None:
                error = "You are not registered to use this API please contact the administrators"
        if not error is None:
            print(error)
            flash(error)
        else:
            session.clear()
            session['user_id'] = user['id']
            if user['username_change_required'] == 1 and user['password_change_required'] == 1:
                session['update_username'] = True 
                session['update_password'] = True
                return redirect(url_for('auth.update_account'))
            if user['username_change_required'] == 1  and user['password_change_required'] == 0:
                session['update_username'] = True
                return redirect(url_for('auth.update_account'))
            if user['username_change_required'] == 0  and user['password_change_required'] == 1:
                session['update_password'] = True
                return redirect(url_for('auth.update_account'))
            return redirect(url_for("index.index"))
    return render_template('auth/login.html')
@bp.route('/update_account', methods = ('GET', 'POST'))
@login_required
def update_account():
    if g.user_status == "admin" or g.user_status == "owner":
        try:
            g.reserved_usernames.remove(g.user_status)
        except:
            pass
    if request.method == "POST":
        password_required = not g.pcr == None
        username_required = not g.ucr ==  None
        print(username_required)
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        old_password = request.form.get('old_password') 
        db = g.user_db
        if username_required: 
            username_error = None
            if new_username is None:
                username_error = "New username is required"
            elif g.user['username'] == new_username.strip().lower():
                username_error = "Username must not be the same as the previous username"
            else:
                #probably needs to be altered at some point to be less annoying 
                new_username = new_username.strip()
                char_array = list(new_username)
                invalidchars = set(string.punctuation.replace("_",""))
                if char_array[0] == "_":
                    username_error = "Username must not start with _"
                elif len(char_array) < g.username_length_min:
                    username_error = "Username must be at least %s characters" % g.username_length_min
                elif len(char_array) > g.username_length_max:
                    username_error = "Username must not be more than %s characters" % g.username_length_max
                char_i = 0
                while username_error is None and char_i < len(char_array):
                    if char_array[char_i] in invalidchars:
                        username_error = "Username must not contain punctuation or special symbol"
                    char_i += 1
                if not new_username.lower() in g.reserved_usernames:
                    if not g.user_status == "owner":
                        contains_reserved = [new_username.lower().find(reserved) for reserved in g.reserved_usernames]
                        sorted_reserved = copy.deepcopy(contains_reserved)
                        sorted_reserved.sort()
                        if -1 != sorted_reserved[-1]:
                            username_error = 'Username must not contain reserved usernames: '
                            for i in range(0,len(contains_reserved)):
                                if contains_reserved[i] == -1:
                                    username_error += g.reserved_usernames[i] + ' '
                            username_error = username_error.rstrip()
                        elif new_username.lower() == "admin" :
                            username_error = "Username must not be reserved username: admin"
                if not db.execute("SELECT id FROM users WHERE username = ?", (new_username,)).fetchone() is None:
                    username_error = "Username already exists please try another"
            if not username_error is None:
                flash(username_error,'username')
                username_error = None
            else:
                query = "UPDATE users SET username = '{username}', username_change_required = 0 WHERE id = {id}".format(
                    username = new_username,
                    id = g.user['id']
                )
                db.execute(query)
                db.commit()
                session.pop('update_username', None)
                g.ucr = None
        if password_required:
            password_error = None
            if new_password is None:
                password_error = "You must enter a new password"
            elif old_password is None:
                password_error = "You must enter your old password"
            elif check_password_hash(g.user['password'], old_password) == False:
                password_error = "Current Password is incorrect"
            elif old_password.lower() == new_password.strip().lower():
                password_error = "New password should not be the same as the old password"
            else:
                new_password = new_password.strip()
                invalidchars = string.punctuation
                for symbol in g.password_symbols:
                    invalidchars = invalidchars.replace(symbol, "")
                invalidchars = set(invalidchars)
                char_new_password = list(new_password)
                if len(char_new_password) < g.password_length_min:
                    password_error = "Password length must not be less than minimum"
                elif len(char_new_password) > g.password_length_max:
                    password_error = "Password length must not be more than maximum"
                char_i = 0
                symbols = False
                uppercase = False
                numbers = False
                while password_error is None and char_i < len(char_new_password):
                    character = char_new_password[char_i]
                    if g.password_symbols_required and character in g.password_symbols:
                        symbols = True
                    elif g.password_uppercase_required and character.isupper():
                        uppercase = True
                    elif g.password_numbers_required:
                        try:
                            int(character)
                            numbers = True
                        except:
                            pass
                    char_i += 1
                if g.password_symbols_required and not symbols:
                    password_error = "Password must contain at least 1 symbol"
                elif g.password_uppercase_required and not uppercase:
                    password_error = "Password must conatain at least 1 uppercase letter "
                elif g.password_numbers_required and not numbers:
                    password_error = "Password must contain at least 1 number"
            if not password_error is None: 
                flash(password_error, 'password')
            else:
                query = "UPDATE users SET password = '{password}' , password_change_required = {pcr} WHERE id = {id}".format(
                    password = generate_password_hash(new_password),
                    pcr = 0,
                    id = g.user['id']
                )
                db.execute(query)
                db.commit()
                session.pop('update_password', None)
                g.pcr = None
    return render_template('auth/update_details.html')
@bp.before_app_request
def load_logged_in_user():
    db, _ = get_db()
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        #load password settings
        g.password_symbols_required = current_app.config['PASSWORD_SYMBOLS_REQUIRED']
        if g.password_symbols_required:
            g.password_symbols = current_app.config['PASSWORD_SYMBOLS']
        g.password_numbers_required = current_app.config['PASSWORD_NUMBERS_REQUIRED']
        g.password_uppercase_required = current_app.config['PASSWORD_UPPERCASE_REQUIRED']
        g.password_length_min = current_app.config['PASSWORD_LENGTH_MIN'] 
        g.password_length_max =  current_app.config['PASSWORD_LENGTH_MAX']
        #load username settings 
        g.reserved_usernames = current_app.config['RESERVED_USERNAMES']
        g.username_length_min = current_app.config['USERNAME_LENGTH_MIN']
        g.username_length_max = current_app.config['USERNAME_LENGTH_MAX']      
        g.ucr = session.get('update_username')
        g.pcr = session.get('update_password')
        g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id, )).fetchone()
        g.user_status = db.execute("SELECT * FROM accessLevels WHERE id = ?", (g.user['access_level_id'],)).fetchone()
        if not g.user['access_decomission_on'] is None:
            if datetime.utcnow() >= datetime.strptime(g.user['access_decomission_on'], '%Y-%m-%d %H:%M:%S'):
                if g.user['access_decomission_to'] is None:
                    query = "UPDATE users SET access_level_id = {aid} WHERE id = {id}".format(
                        aid = "(SELECT id FROM accessLevels WHERE access_level = 'open')",
                        id = user_id
                    )
                    db.execute(query)
                    db.commit()
                    g.user_status = 'open'
                    g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id, )).fetchone()
                else:
                    query = "UPDATE users SET access_level_id = ? WHERE id = ? "
                    db.execute(query,(g.user['access_decomission_to'], user_id))
                    db.commit()
                    g.user_status = db.execute("SELECT access_level FROM accessLevels WHERE id = ?", (g.user['access_decomission_to'],)).fetchone() 
                    g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        if g.user_status != 'open' and not g.user_status['decomission_on'] is None:
            if datetime.utcnow() >= datetime.strptime(g.user_status['decomission_on'], '%Y-%m-%d %H:%M:%S'):
                non_decomissioned = False
                while not non_decomissioned:
                    if g.user_status['decomission_to'] is None:
                        db.execute("UPDATE users SET access_level_id = {ali} WHERE id = {id}".format(
                            ali = "(SELECT id From accessLevels WHERE access_level = 'open')",
                            id = user_id
                        ))
                        db.commit()
                        g.user_status = 'open'
                        non_decomissioned = True
                    else:
                        g.user_status = db.execute('SELECT * FROM accessLevels WHERE id = ?', (g.user_status['decomission_to'],)).fetchone()
                        if not  g.user_status['decomission_on'] is None:
                            if datetime.utcnow() < datetime.strptime(g.user_status['decomission_on'], '%Y-%m-%d %H:%M:%S'):
                                db.execute("UPDATE users SET access_level_id = ? WHERE id = ?", (g.user_status['id'], user_id))
                                db.commit()
                                g.user_status = g.user_status['access_level']
                                g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                                non_decomissioned = True 
                        else:
                            db.execute("UPDATE users SET access_level_id = ? WHERE id = ?", (g.user_status['id'],user_id))
                            db.commit()
                            g.user = db.execute("SELECT * FROM users WHERE id = ?",(user_id,)).fetchone()
                            g.user_status = g.user_status['access_level']
                            non_decomissioned = True 
        elif g.user_status != 'open' and g.user_status['decomission_on'] is None:
            db.execute("UPDATE users SET access_level_id = ? WHERE id = ?", (g.user_status['id'],user_id))
            db.commit()
            g.user = db.execute("SELECT * FROM users WHERE id = ?",(user_id,)).fetchone()
            g.user_status = g.user_status['access_level']
        elif g.user_status is None:
            query = "UPDATE users SET access_level_id = {aid} WHERE id = {id}".format(
                aid = "(SELECT id FROM accessLevels WHERE access_level = 'open')",
                id = user_id
            )
            db.execute(query)
            db.commit()
            g.user = db.execute("SELECT * FROM users WHERE id = ?",(user_id,))
            g.user_status = 'open'
        if g.user_status != 'open' and g.user_status != 'restricted' and g.user_status != 'owner' and g.user_status != 'admin' and g.user_status != 'deactivated':
            query = "SELECT id, access_level FROM accessLevels WHERE id = {id}".format(
                   id = "(SELECT equivelent_to FROM accessLevels WHERE access_level = '{ac}')".format(
                       ac = g.user_status
                   )
               )
            equivalence = db.execute(query).fetchone()
            if equivalence is None:
                g.user_status = 'open'
                query = "UPDATE accessLevels SET equivelent_to = {eq} WHERE id = {id}".format(
                    eq = "(SELECT id FROM accessLevels WHERE access_level = 'open')",
                    id = user_id
                )
            else:
                g.user_status = equivalence['access_level']
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))