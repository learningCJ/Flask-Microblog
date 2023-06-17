from app import db, login
from flask import current_app
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
from time import time
from app.search import add_to_index, remove_from_index, query_index

@login.user_loader
def user_loader(id):
    return db.session.get(User,int(id))

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [],0
            #return cls.query.filter_by(id=0), 0
        when = {}
        for i in range(len(ids)):
            when[ids[i]] = i
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total
    
    @classmethod
    def before_commit(cls, session):
        session._changes={
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__,obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = db.Table(
    "followers",
    db.metadata, 
    sa.Column('follower_id', sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index = True, unique = True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index = True, unique = True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author', passive_deletes = True)
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[datetime] = so.mapped_column(default = datetime.utcnow)
    isVerified: so.Mapped[bool] = so.mapped_column()

    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=followers.c.follower_id == id,
        secondaryjoin=followers.c.followed_id == id,
        back_populates="followers"
    )

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=followers.c.followed_id==id,
        secondaryjoin=followers.c.follower_id==id,
        back_populates="following"
    )

    def is_verified(self):
        return db.session.scalar(sa.select(User.isVerified).where(User.id == self.id))

    def verify(self):
        self.isVerified = True

    def is_following(self,user):
        return db.session.scalars(sa.select(User).where(
            User.id == self.id, User.following.contains(user))).one_or_none() is not None
    
    def follow(self,user):
        if not self.is_following(user):
            db.session.execute(sa.insert(followers).values(
                follower_id=self.id, followed_id=user.id))

    def unfollow(self,user):
        if self.is_following(user):
            db.session.execute(sa.delete(followers).where(
                followers.c.follower_id == self.id,
                followers.c.followed_id == user.id))
            
    def followed_posts_select(self):
        Author = so.aliased(User)
        return sa.select(Post).join(Post.author.of_type(Author)).join(
            Author.followers, isouter=True).group_by(Post).where(
            sa.or_(Post.author == self, User.id == self.id))        
    
    def count_following(self):
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            self.following.select().subquery()))
    
    def count_followers(self):
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest,size)
    
    def get_register_reset_password_token(self, expires_in=600):
        return jwt.encode({'user_id': self.id, 'exp':time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['user_id']
        except:
            return
        return db.session.get(User, id)
    
    def __repr__(self) -> str:
        return "<User: {} >".format(self.username)

class Post(SearchableMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(1500))
    timestamp: so.Mapped[datetime] = so.mapped_column(index = True, default=datetime.utcnow)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index = True)
    author: so.Mapped['User'] = so.relationship(back_populates='posts')
    language: so.Mapped[str] = so.mapped_column(sa.String(10))

    __searchable__ = ['body']
    
    def delete(self):
        db.session.execute(sa.delete(Post).where(Post.id == self.id))

    def __repr__(self):
        return '<Post: {}>'.format(self.body)

class TechStack(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    techType: so.Mapped[str] = so.mapped_column(sa.String(50))
    techName: so.Mapped[str] = so.mapped_column(sa.String(100))
    category: so.Mapped[str] = so.mapped_column(sa.String(20))

    def __repr__(self):
        return '<{type}: {name}>'.format(type=self.techType, name=self.techName)
    
    def delete(self):
        db.session.execute(sa.delete(TechStack).where(TechStack.id == self.id))
