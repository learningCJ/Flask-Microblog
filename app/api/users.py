from app.api import bp
from flask import jsonify, request, url_for, abort
from app.models import User
from app import db
import sqlalchemy as sa
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.auth.validators import pwPolicy
import json
from wtforms.validators import  ValidationError


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(db.get_or_404(User,id).to_dict())

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(sa.select(User), page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page',1,type=int)
    per_page = min(request.args.get('per_page', 10, type=int),100)
    data = User.to_collection_dict(user.followers.select(), page, per_page, 'api.get_followers', id=id)
    return jsonify(data)

@bp.route('/users/<int:id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id): 
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int),100)
    data = User.to_collection_dict(user.following.select(), page, per_page, 'api.get_following', id=id)
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include username, email, and password fields')
    if db.session.scalar(sa.select(User).filter_by(username=data['username'])):
        return bad_request('please use a different username')
    if db.session.scalars(sa.select(User).filter_by(email=data['email'])).first():
        return bad_request('Please use a different email address')
    try:
        pwPolicy(data=data["password"])
    except ValidationError as e:
        return bad_request(str(e))
    user = User()
    user.from_dict(data, pw_included=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    pw_included=False
    user = db.get_or_404(User,id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
        db.session.scalar(sa.select(User).filter_by(username=data['username'])):
        return bad_request('Please use a different username')
    if 'email' in data and data['email'] != user.email and \
        db.session.scalar(sa.select(User).filter_by(email=data['email'])):
        return bad_request('Please use a different email address')
    if 'email' in data and data['email'] != user.email and user.isVerified:
        return bad_request('You cannot update the email once confirmed')
    if 'password' in data:
        pw_included = True
        try:
            pwPolicy(data=data["password"])
        except ValidationError as e:
            return bad_request(str(e))
    user.from_dict(data, pw_included=pw_included)
    db.session.commit()
    return jsonify(user.to_dict())
