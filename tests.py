import unittest
from app import create_app, db
from app.models import User, Post
import sqlalchemy as sa
from datetime import datetime, timedelta
from config import Config
from langdetect import detect, LangDetectException

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username="test")
        u.set_password('CorrectPassword')
        self.assertFalse(u.check_password('WrongPassword'))
        self.assertTrue(u.check_password('CorrectPassword'))

    def test_avatar(self):
        u = User(username="john", email="john@example.com")
        self.assertEqual(u.avatar(128), 'https://www.gravatar.com/avatar/'
                                        'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128')
        
    def test_follow(self):
        u1 = User(username="Susan", email="susan@example.com")
        u2 = User(username="David", email="david@example.com")
        db.session.add_all([u1,u2])
        db.session.commit()

        assert db.session.scalars(u1.following.select()).all() == []
        assert db.session.scalars(u2.following.select()).all() == []

        for _ in range(2):
            u1.follow(u2)
            db.session.commit()

            assert u1.count_following() == 1
            assert db.session.scalar(u1.following.select()).username == "David"
            assert u2.count_following() == 0
            assert u2.count_followers() == 1
            assert db.session.scalar(u2.followers.select()).username == "Susan"
            
        for _ in range(2):
            u1.unfollow(u2)
            db.session.commit()

            assert not u1.is_following(u2)
            assert not u2.is_following(u1)

            assert u1.count_following() == 0
            assert u2.count_followers() == 0
            assert db.session.scalars(u1.following.select()).all() == []
            assert db.session.scalars(u2.followers.select()).all() == []

    def test_following(self):
        u1 = User(username="Summer", email="summer@c137.com")
        u2 = User(username="Morty", email="morty@c137.com")
        u3 = User(username="Beth", email="beth@c137.com")
        u4 = User(username="Rick", email ="iamgod@c134.com")
        db.session.add_all([u1,u2,u3,u4])

        now = datetime.utcnow()

        p1 = Post(body="Post from Summer", author=u1, timestamp=now+timedelta(seconds=1), language='en')
        p2 = Post(body="Post from Morty", author=u2, timestamp=now+timedelta(seconds=4), language='en')
        p3 = Post(body="Wine memes from Beth", author=u3, timestamp=now+timedelta(seconds=2), language='en')
        p4 = Post(body="I am so smart I am god for I am Rick", author=u4, timestamp=now+timedelta(seconds=3), language='en')
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        u1.follow(u4)
        u2.follow(u4)
        u3.follow(u1)
        u3.follow(u2)
        u3.follow(u4)
        db.session.commit()

        f1 = db.session.scalars(u1.followed_posts_select().order_by(Post.timestamp.desc())).all()
        f2 = db.session.scalars(u2.followed_posts_select().order_by(Post.timestamp.desc())).all()
        f3 = db.session.scalars(u3.followed_posts_select().order_by(Post.timestamp.desc())).all()
        f4 = db.session.scalars(u4.followed_posts_select().order_by(Post.timestamp.desc())).all()
        

        assert f1 == [p4,p1]
        assert f2 == [p2, p4]
        assert f3 == [p2, p4, p3, p1]
        assert f4 == [p4]
      
if __name__=="__main__":
    unittest.main(verbosity=2)
