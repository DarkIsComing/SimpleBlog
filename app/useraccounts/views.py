from flask import redirect, render_template, url_for, request, g, flash, session
from .. import db

def index():
    return 'hello!'
