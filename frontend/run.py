#!../venv/bin/python
from app import webapp

if __name__=="__main__":
    webapp.run('0.0.0.0',5000, debug=False)



