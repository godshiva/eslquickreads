from flask import render_template
from eslquickreads import app


# @app.errorhandler(401)
# def page_not_found(e):
#     # note that we set the 401 status explicitly
#     return render_template('errors/401.html'), 401
#
#
# @app.errorhandler(403)
# def page_not_found(e):
#     # note that we set the 403 status explicitly
#     return render_template('errors/403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('errors/500.html'), 500
