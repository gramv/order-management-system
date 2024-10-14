
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    size = StringField('Size')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    wholesaler = SelectField('Wholesaler', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Product')

class BulkUploadForm(FlaskForm):
    file = FileField('Excel File', validators=[
        FileAllowed(['xlsx'], 'Please upload only Excel files (.xlsx)'),
        DataRequired()
    ])
    submit = SubmitField('Upload Products')

class WholesalerForm(FlaskForm):
    name = StringField('Wholesaler Name', validators=[DataRequired()])
    is_daily = BooleanField('Is Daily Wholesaler')
    contact_person = StringField('Contact Person')
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    submit = SubmitField('Submit')


class OrderListForm(FlaskForm):
    product = StringField('Product', validators=[DataRequired()])
    product_id = HiddenField('Product ID')
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Order')