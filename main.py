import os
from flask import Flask
from backend.routes import init_routes
from dotenv import load_dotenv

app=Flask(__name__, template_folder="frontend/templates")

load_dotenv()
app.config["SECRET_KEY"]=os.getenv("SECRET_KEY")

# router 등록
init_routes(app)

if __name__=="__main__":
    app.run(debug=True)