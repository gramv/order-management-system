# app/cli.py
import click
from flask.cli import with_appcontext
from app import db
from app.models import User

def register_commands(app):
    app.cli.add_command(create_owner)

@click.command('create-owner')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_owner(username, email, password):
    """Create an owner user"""
    try:
        user = User(
            username=username,
            email=email,
            role='owner'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Owner user {username} created successfully!')
    except Exception as e:
        click.echo(f'Error creating owner user: {str(e)}')
        db.session.rollback()
        