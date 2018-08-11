from flask import Blueprint
from . import views
from ..main import errors

accounts = Blueprint('useraccounts', __name__)

accounts.add_url_rule('/login/', 'login', views.login, methods=['GET', 'POST'])
accounts.add_url_rule('/register/', 'register', views.register, methods=['GET', 'POST'])
accounts.add_url_rule('register/admin', 'register_admin', views.register, defaults={'admin_create': True},
                      methods=['GET', 'POST'])
accounts.add_url_rule('/logout/', 'logout', views.logout)
accounts.add_url_rule('/users/', view_func=views.Users.as_view('users'))
accounts.errorhandler(403)(errors.handle_forbidden)
