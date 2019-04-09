from flask_basicauth import BasicAuth
import base64
from flask import current_app, session, g, request, Response
from datetime import datetime
from werkzeug.security import check_password_hash
from db import get_db
import functools
bauth = None
class IntegratedBasicAuth(BasicAuth):
    def __init__(self,app):
        super(IntegratedBasicAuth,self).__init__(app)
    #overiding the check credentials method
    def required(self, view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            if self.check_login():
                if g.user_status == 'deactivated':
                    return Response('Account has been deactivated please contact admin', 403)
                else:
                    return view_func(*args,**kwargs)
            else:
                if self.authenticate():
                    return view_func(*args,**kwargs)
                else:
                    return self.challenge() 
        return wrapper
    def check_credentials(self,username,password):
        db,_ = get_db()
        query = "SELECT * FROM users WHERE username = '{username}'".format(
            username = username
        )
        res = db.execute(query).fetchone()
        if res is None:
            return False
        else:
            return check_password_hash(res['password'], password)

    def check_login(self):
        db, _ = get_db()
        user_id = session.get('user_id')
        if user_id is None:
            return False
        else:
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
        return True
def init_app(app):
    global bauth 
    bauth = IntegratedBasicAuth(app = app)