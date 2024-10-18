from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, FloatField, BooleanField, SubmitField, IntegerField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, NumberRange, Email, Optional
from flask_wtf.file import FileField, FileAllowed

class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    size = StringField('Size')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    wholesaler = SelectField('Wholesaler', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

# Keep your other form classes (WholesalerForm, OrderListForm, etc.) as they were

class WholesalerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    is_daily = BooleanField('Is Daily Wholesaler')
    contact_person = StringField('Contact Person', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    submit = SubmitField('Submit')

class OrderListItemForm(FlaskForm):
    product = IntegerField('Product', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    comment = StringField('Comment')

class OrderListForm(FlaskForm):
    product_search = StringField('Product', validators=[DataRequired()])
    product_id = HiddenField('Product ID')
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Order')

class BulkUploadForm(FlaskForm):
    file = FileField('Excel File', validators=[
        FileAllowed(['xlsx'], 'Please upload only Excel files (.xlsx)'),
        DataRequired()
    ])
    submit = SubmitField('Upload Products')

class CustomerOrderForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    customer_contact = StringField('Customer Contact', validators=[DataRequired()])
    is_paid = BooleanField('Paid')
    submit = SubmitField('Create Order')

class CustomerOrderItemForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add Item')