from flask import (
    Blueprint, render_template, current_app,
    flash, redirect, url_for,
    abort, jsonify, request,
)

#from handlink.models import Models
#from handlink.ext.db import db
#from handlink.forms.main import Forms
bp_user = Blueprint("user", __name__)