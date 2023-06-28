from app.api import bp

@bp.route('/users/<int:id>', method=['GET'])
def get_user(id):
    pass

@bp.route('/users', methods=['GET'])
def get_users():
    pass

@bp.route('/users/<int:id>/followers', method=['GET'])
def get_followers(id):
    pass

@bp.route('/users/<int:id>/followed', method=['GET'])
def get_followed(id): #rename to following?
    pass

@bp.route('/users', method=['POST'])
def create_user():
    pass

@bp.route('/users/<int:id>', method=['POST'])
def update_user():
    pass
