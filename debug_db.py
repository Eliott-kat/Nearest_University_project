
from app import app, db

with app.app_context():
    # SQLAlchemy 2.x: use db.inspect for table names
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        print('Tables:', inspector.get_table_names())
        # Delete demo user if exists
        db.session.execute(text("DELETE FROM users WHERE email='demo@acadcheck.local'"))
        db.session.commit()
        print('Demo user deleted if existed.')
    except Exception as e:
        print('Error listing tables or deleting demo user:', e)
    try:
        users = db.session.execute(text('SELECT * FROM users')).fetchall()
        print('Users:', users)
    except Exception as e:
        print('Error reading users table:', e)
