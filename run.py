from app import create_app, db
from app.models import User, Product, Wholesaler

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Wholesaler': Wholesaler}

if __name__ == '__main__':
    app.run()