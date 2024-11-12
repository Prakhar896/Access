from flask import Flask, request, render_template, url_for, redirect, session
from models import Identity, Logger, Universal
import os, functools, time, datetime
from dotenv import load_dotenv
load_dotenv()

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        if not os.environ.get("DECORATOR_DEBUG_MODE", "False") == "True":
            return func(*args, **kwargs)
        
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(value)}")
        return value
    return wrapper_debug

def slow_down(_func=None, *, rate=1):
    """Sleep given amount of seconds before calling the function"""
    def decorator_slow_down(func):
        @functools.wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            time.sleep(rate)
            return func(*args, **kwargs)
        return wrapper_slow_down

    if _func is None:
        return decorator_slow_down
    else:
        return decorator_slow_down(_func)
    
def cache(func):
    """Keep a cache of previous function calls"""
    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper_cache.cache:
            wrapper_cache.cache[cache_key] = func(*args, **kwargs)
        return wrapper_cache.cache[cache_key]
    wrapper_cache.cache = {}
    return wrapper_cache

def jsonOnly(func):
    """Enforce the request to be in JSON format. 400 error if otherwise."""
    @functools.wraps(func)
    @debug
    def wrapper_jsonOnly(*args, **kwargs):
        if not request.is_json:
            return "ERROR: Invalid request format.", 400
        else:
            return func(*args, **kwargs)
    
    return wrapper_jsonOnly

def checkAPIKey(func):
    """Check if the request has the correct API key. 401 error if otherwise."""
    @functools.wraps(func)
    @debug
    def wrapper_checkAPIKey(*args, **kwargs):
        if ("APIKey" in os.environ) and (("APIKey" not in request.headers) or (request.headers["APIKey"] != os.environ.get("APIKey", None))):
            return "ERROR: Request unauthorised.", 401
        else:
            return func(*args, **kwargs)
    
    return wrapper_checkAPIKey

def enforceSchema(*expectedArgs):
    """Enforce a specific schema for the JSON payload.
    
    Requires request to be in JSON format, or 415 werkzeug.exceptions.BadRequest error will be raised.
    
    Sample implementation:
    ```python
    @app.route("/")
    @enforceSchema(("hello", int), "world", ("john"))
    def home():
        return "Success!"
    ```
    
    The above implementation mandates that 'hello', 'world' and 'john' attributes must be present. Additionally, 'hello' must be an integer.
    
    Parameter definition can be one of the following:
    - String: Just ensures that the parameter is present, regardless of its value's datatype.
    - Tuple, with two elements: First element is the parameter name, second element is the expected datatype.
        - If the datatype (second element) is not provided, it will be as if the parameter's name was provided directly, i.e. it will just ensure that the parameter is present.
        - Example: `("hello", int)` ensures that 'hello' is present and is an integer. But, `("hello")` ensures that 'hello' is present, but does not enforce any datatype.
        
    Raises `"ERROR: Invalid request format", 400` if the schema is not met.
    """
    def decorator_enforceSchema(func):
        @functools.wraps(func)
        @debug
        def wrapper_enforceSchema(*args, **kwargs):
            jsonData = request.get_json()
            for expectedTuple in expectedArgs:
                if isinstance(expectedTuple, tuple):
                    if expectedTuple[0] not in jsonData:
                        return "ERROR: Invalid request format.", 400
                    if len(expectedTuple) > 1:
                        if not isinstance(jsonData[expectedTuple[0]], expectedTuple[1]):
                            return "ERROR: Invalid request format.", 400
                elif expectedTuple not in jsonData:
                    return "ERROR: Invalid request format.", 400
            
            return func(*args, **kwargs)
        
        return wrapper_enforceSchema
    
    return decorator_enforceSchema

def checkSession(_func=None, *, strict=False, provideIdentity=False):
    def decorator_checkSession(func):
        @functools.wraps(func)
        @debug
        def wrapper_checkSession(*args, **kwargs):
            # Helper function to handle return cases
            def handleReturn(msg: str, code: int, user: Identity | None=None, clearSessionForErrorCodes: bool = True):                
                if code != 200 and clearSessionForErrorCodes and len(session.keys()) != 0:
                    session.clear()
                
                if code != 200 and strict:
                    return msg, code
                elif provideIdentity and user != None:
                    return func(user, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            # List of required parameters in a session
            requiredParams = ["username", "authToken", "sessionStart"]
            
            # Check if session parameters match up
            if len(session.keys()) != len(requiredParams):
                return handleReturn("ERROR: Invalid session.", 401)
            
            # Check if session is corrupted
            for param in requiredParams:
                if param not in session:
                    return handleReturn("ERROR: Invalid session.", 401)
            
            # If strict mode, verify the session by trying to load the user based on it.
            user = None
            if strict or provideIdentity:
                try:
                    # Load the user by passing in the session's authToken
                    user = Identity.load(authToken=session["authToken"])
                    if not isinstance(user, Identity):
                        # If the user was not found, reset the session and return an error.
                        return handleReturn("ERROR: Invalid session.", 401)
                except Exception as e:
                    Logger.log("CHECKSESSION ERROR: Failed to load user for strict auth token verification. Error: {}".format(e))
                    return handleReturn("ERROR: Invalid session.", 401)
                    
                try:
                    # Check the session start time for expiration cases
                    if not isinstance(user.lastLogin, str):
                        return handleReturn("ERROR: Invalid session.", 401)
                    if (Universal.utcNow() - Universal.fromUTC(user.lastLogin)).total_seconds() > 7200:
                        ## Session expired
                        user.authToken = None
                        user.save()
                        return handleReturn("ERROR: Session expired.", 401)
                except Exception as e:
                    Logger.log("CHECKSESSION ERROR: Failed to process session expiration status. Error: {}".format(e))
                    return handleReturn("ERROR: Invalid session.", 401)
            
            # Let handleReturn handle the success case
            return handleReturn("SUCCESS: Session verified.", 200, user)
        
        return wrapper_checkSession

    if _func is None:
        return decorator_checkSession
    else:
        return decorator_checkSession(_func)