import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    from app.models import *
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
