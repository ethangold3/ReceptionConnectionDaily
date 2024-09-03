from flask import Flask
from flask_talisman import Talisman
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

csp = {
    'default-src': [
        "'self'",
        'https://code.jquery.com',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
    ],
    'script-src': [
        "'self'",
        'https://code.jquery.com',
        "'unsafe-inline'",
        "'unsafe-eval'",
    ],
    'style-src': [
        "'self'",
        'https://code.jquery.com',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
        "'unsafe-inline'",
    ],
    'font-src': [
        "'self'",
        'https://fonts.gstatic.com',
    ],
    'img-src': ["'self'", 'data:'],
}

Talisman(app, force_https=True, content_security_policy=csp)

from app import routes