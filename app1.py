# Flask
import sys
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Twisted!"

# Twisted
from flask_script import Manager
from flask_twisted import Twisted
from twisted.python import log

# Main
if __name__ == "__main__":

    twisted = Twisted(app)
    log.startLogging(sys.stdout)

    app.logger.info(f"Running the app...")

    manager = Manager(app)
    manager.run()
