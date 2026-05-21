from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = 'admin'
    correct_password = 'password'
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# the middleware, authenticate, implements basic authentication. It checks the provided credentials against predefined values
#  and raises an HTTPException if the authentication fails. 
# This middleware can be applied to any endpoint that requires authentication by using the Depends function.
# what is the depends function doing here? 
#The Depends function is a dependency injection system provided by FastAPI. It allows you to declare dependencies for your endpoint functions.
# In this case, the authenticate function is declared as a dependency for any endpoint that requires authentication. 
#When an endpoint is called, FastAPI will automatically call the authenticate function and pass the necessary credentials to it. 
#If the authentication is successful, the endpoint will proceed; otherwise, it will return an unauthorized error.
# keyword is dependency checkpoint here