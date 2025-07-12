from flask import Flask
from backend.routes import init_routes

app=Flask(__name__, template_folder="frontend/templates")

app.config["SECRET_KEY"]="abc123"

# router 등록
init_routes(app)

if __name__=="__main__":
    app.run(debug=True)
