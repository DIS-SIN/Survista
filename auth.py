import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import string
from datetime import datetime 
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db 
bp = Blueprint('auth', __name__, url_prefix='/auth')
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
            return "<p> you're logged in </p>"
    return render_template('auth/login.html')
@bp.route('/update_account', methods = ('GET', 'POST'))
@login_required
def update_account():
    if request.method == "GET":
        if g.pcr is None and g.ucr is None:
            return render_template('auth/contact_admin.html')
        else:
            return render_template('auth/update_details.html')
    elif request.method == "POST":
        try:
            g.reserved_usernames.remove
        password_required = not g.pcr is None
        username_required = not g.ucr is None
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        old_password = request.form.get('old_password') 
        db = g.user_db
        error = None
        if username_required: 
            if new_username is None:
                error = "New username is required"
            else:
                #probably needs to be altered at some point to be less annoying 
                new_username = new_username.strip()
                char_array = new_username.split()
                invalidchars = set(string.punctuation.replace("_",""))
                if char_array[0] == "_":
                    error = "Username must not start with _"
                elif len(char_array) < g.username_length_min:
                    error = "Username must be at least %s characters" % g.username_length_min
                elif len(char_array) > g.username_length_max:
                    error = "Username must not be more than %s characters" % g.username_length_max
                char_ i = 0
                while error is None and char_i < len(char_array):
                    if char_array[char_i] in invalidchars:
                        error = "Username must not contain punctuation or special symbol"
                    char_i += 1
                if not (new_username.lower() in g.reserved_usernames or g.user_status in g.reserved_usernames)
                    contains_reserved = [new_username.lower().find(reserved) for reserved in g.reserved_usernames]
                    error = 'Username must not contain reserved usernames: '
                    for i in range(0,len(contains_reserved)):
                        if contains_reserved[i] == -1:
                            error += g.reserved_usernames[i] + ' '
                    error = error.rstrip()
                elif g.user_status in g.reserved_usernames
                    error = "username must not contain or be a reserved username: %s " % new_username
                if g.user['username'] == new_username:
                    error = "Username must not be the same as the previous username"
                if not db.execute("SELECT id FROM users WHERE username = ?", (new_username,)).fetchone() is None:
                    error = "Username already exists please try another"
        elif password_required and (new_password is None or old_password is None):
            error = "Please enter your current password and a new password"
        if username_required and new_username is None:
            error = "Please enter your new username"
@bp.before_app_request
def load_logged_in_user():
    db, _ = get_db()
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.ucr = session.get('update_username')
        g.pcr = session.get('update_password')
        g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id, )).fetchone()
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
        if g.user_status != 'open' or g.user_status != 'restricted' or g.user_status != 'owner' or g.user_status != 'admin' or g.user_status != 'deactivated':
            query = "SELECT id, access_level FROM accessLevels WHERE id = {id}".format(
                   id = "(SELECT equivelent_to FROM accessLevels WHERE access_level = '{ac}')".format(
                       id = g.user_status
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