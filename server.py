from flask import Flask, render_template
from cleanup.routes import cleanup_bp  # ✅ import the blueprint

app = Flask(__name__)  # ✅ create the app BEFORE using it

# Register the cleanup blueprint
app.register_blueprint(cleanup_bp, url_prefix="/api")

# Example root route
@app.route("/")
def home():
    return render_template("cleanup.html")

if __name__ == "__main__":
    app.run(debug=True,port=5001)
