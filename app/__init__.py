from flask import Flask

import config

def createApp(configClass = config.Config):
    app = Flask(__name__)
    app.config.from_object(configClass)

    # flask extentions go here
    
    # register blueprints here
    from app.login import bp as loginbp
    app.register_blueprint(loginbp)

    return app