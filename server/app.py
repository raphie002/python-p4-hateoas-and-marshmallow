#!/usr/bin/env python3
# server/app.py
from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_restful import Api, Resource # type: ignore
from marshmallow import validate, ValidationError # type: ignore
from models import db, Newsletter, Comment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Initialize Marshmallow AFTER db.init_app
ma = Marshmallow(app)
api = Api(app)

# --- SCHEMAS ---

class CommentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Comment
        load_instance = True
    
    id = ma.auto_field()
    text = ma.auto_field(validate=validate.Length(min=1))

class NewsletterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Newsletter
        load_instance = True

    # Validation: Title must be 5-50 chars, Body min 10
    title = ma.auto_field(validate=validate.Length(min=5, max=50))
    body = ma.auto_field(validate=validate.Length(min=10))
    published_at = ma.auto_field()

    # Nesting: Show comments inside the newsletter
    comments = ma.Nested(CommentSchema, many=True)

    # HATEOAS: Hyperlinks for navigation
    url = ma.Hyperlinks({
        "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
        "collection": ma.URLFor("newsletters")
    })

# Instantiate schemas
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# --- ROUTES ---

class Index(Resource):
    def get(self):
        return make_response({"index": "Welcome to the HATEOAS API"}, 200)

class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(newsletters_schema.dump(newsletters), 200)

    def post(self):
        try:
            # Validate data from the request
            data = newsletter_schema.load(request.form)
            
            new_newsletter = Newsletter(
                title=data['title'],
                body=data['body']
            )
            db.session.add(new_newsletter)
            db.session.commit()
            
            return make_response(newsletter_schema.dump(new_newsletter), 201)
        except ValidationError as err:
            return make_response(err.messages, 400)

class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"error": "Newsletter not found"}, 404)
        return make_response(newsletter_schema.dump(newsletter), 200)

    def patch(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"error": "Newsletter not found"}, 404)
        
        try:
            # Partial=True allows updating only some fields
            data = newsletter_schema.load(request.form, partial=True)
            for attr, value in data.items():
                setattr(newsletter, attr, value)
            
            db.session.commit()
            return make_response(newsletter_schema.dump(newsletter), 200)
        except ValidationError as err:
            return make_response(err.messages, 400)

    def delete(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"error": "Newsletter not found"}, 404)
        
        db.session.delete(newsletter)
        db.session.commit()
        return make_response({"message": "Deleted successfully"}, 200)

api.add_resource(Index, '/')
api.add_resource(Newsletters, '/newsletters')
api.add_resource(NewsletterByID, '/newsletters/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)