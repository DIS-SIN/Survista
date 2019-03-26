def verify(app):
    verify_username_constraints(app)
    verify_password_constraints(app)

def verify_username_constraints(app):
    username_length_min = app.config.get('USERNAME_LENGTH_MIN')
    username_length_max = app.config.get('USERNAME_LENGTH_MAX')
    username_symbols_required = app.config.get('USERNAME_SYMBOLS_REQUIRED')
    username_symbols = app.config.get('USERNAME_SYMBOLS_ALLOWED')
    username_uppercase_required = app.config.get('USERNAME_UPPERCASE_REQURIED')

    #check if symbols are required and if symbols do not exist raise an error
    if username_symbols_required == True:
        if username_symbols is None:
            raise ValueError("USERNAME_SYMBOLS_REQUIRED was set to be true however no username_SYMBOLS_ALLOWED were")
    else:
        app.config['USERNAME_SYMBOLS_REQUIRED'] = False
    
    #check if symbols exist and it is a string
    #if it exists but is not a string throw an error
    if not isinstance(username_symbols, (str, None)):
        raise TypeError(f"USERNAME_SYMBOLS_ALLOWED must be str not {type(username_symbols)} ")
    elif username_symbols is not None:
        app.config['USERNAME_SYMBOLS_ALLOWED'] = list(username_symbols)
    else:    
        app.config['USERNAME_SYMBOLS_ALLOWED'] = False

    #See if the username uppercase requirement has been set otherwise set to false
    if isinstance(username_uppercase_required, (None, bool)):
        app.config["USERNAME_UPPERCASE_REQUIRED"] = username_uppercase_required or False 
    else:
        TypeError(f"USERNAME_UPPERCASE_REQUIRED must be of type bool not {type(username_uppercase_required)}")
    
    #username length min
    if not isinstance(username_length_min, (int, None)):
        raise TypeError(f'USERNAME_LENGTH_MIN must be of type int or None not {type(username_length_min)}')
    elif username_length_min is not None and username_length_min > 8 or username_length_min < 4:
        raise ValueError('USERNAME_LENGTH_MIN must be between the values of 4 and 16')
    elif username_length_min is None:
        username_length_min = 5
        app.config['USERNAME_LENGTH_MIN'] = 5
    
    #username length max
    if not isinstance(username_length_max, (int, None)):
        raise TypeError(f'USERNAME_LENGTH_MAX must be of type None or int not {type(username_length_max)}')    
    elif isinstance(username_length_max, int) and username_length_max > 20 or username_length_max < 8:
        raise ValueError('USERNAME_LENGTH_MAX must be between the values of 8 and 32')
    elif username_length_max is None:
        username_length_max = 10
        app.config['USERNAME_LENGTH_MAX'] = 10
    
    if username_length_max < username_length_min:
        raise ValueError("USERNAME_LENGTH_MAX must be greater than USERNAME_LENGTH_MIN")

def verify_password_constraints(app):
    password_length_min = app.config.get('PASSWORD_LENGTH_MIN')
    password_length_max = app.config.get('PASSWORD_LENGTH_MAX')
    password_symbols_required = app.config.get("PASSWORD_SYMBOLS_REQUIRED")
    password_symbols = app.config.get('PASSWORD_SYMBOLS_ALLOWED')
    password_uppercase_required = app.config.get('PASSWORD_UPPERCASE_REQUIRED')
    ###password checks###

    #check if symbols are required of so load the allowed symbols 
    if password_symbols_required == True:
        if password_symbols is None:
            raise ValueError("PASSWORD_SYMBOLS_REQUIRED was set to be true however no PASSWORD_SYMBOLS_ALLOWED were")
    else:
        app.config['PASSWORD_SYMBOLS_REQUIRED'] = False
    
    #check if symbols exist and it is a string
    #if it exists but is not a string throw an error
    if not isinstance(password_symbols, (str,None)):
        raise TypeError(f"PASSWORD_SYMBOLS_ALLOWED must be str not {type(password_symbols)}")
    elif password_symbols is not None:
        app.config['PASSWORD_SYMBOLS_ALLOWED'] = list(password_symbols)
    else:
        app.config['PASSWORD_SYMBOLS_ALLOWED'] = False

    
    #See if the password uppercase requirement has been set otherwise set to false
    if isinstance(password_uppercase_required, (None, bool)):
        app.config["PASSWORD_UPPERCASE_REQUIRED"] = password_uppercase_required or False 
    else:
        TypeError(f"PASSWORD_UPPERCASE_REQUIRED must be of type bool not {type(password_uppercase_required)}")

    #password_length_min
    if not isinstance(password_length_min, (int, None)):
        raise TypeError(f'PASSWORD_LENGTH_MIN must be of type int or None not {type(password_length_min)}')
    elif password_length_min is not None and password_length_min > 16 or password_length_min < 4:
        raise ValueError('PASSWORD_LENGTH_MIN must be between the values of 4 and 16')
    elif password_length_min is None:
        password_length_min = 8
        app.config['PASSWORD_LENGTH_MIN'] = 8

    #password_length_max
    if not isinstance(password_length_max, (int, None)):
        raise TypeError(f'PASSWORD_LENGTH_MAX must be of type None or int not {type(password_length_max)}')    
    elif isinstance(password_length_max, int) and password_length_max > 32 or password_length_max < 10:
        raise ValueError('PASSWORD_LENGTH_MAX must be between the values of 8 and 32')
    elif password_length_max is None:
        password_length_max = 20
        app.config['PASSWORD_LENGTH_MAX'] = 20


    if password_length_max < password_length_min:
        raise ValueError('PASSWORD_LENGTH_MAX must be greater than PASSWORD_LENGTH_MIN')