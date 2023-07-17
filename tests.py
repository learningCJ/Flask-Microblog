import unittest
from app import create_app, db
from app.models import User, Post, Article, Tag, Comment
import sqlalchemy as sa
from datetime import datetime, timedelta
from config import Config
from langdetect import detect, LangDetectException

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL=''

class Blogging_Feature_Test(unittest.TestCase):
    #let's figure out what the logical breakup of this is
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_tag(self):
        #Add users
        u1 = User(username="Summer", email="summer@c137.com", isVerified=1)
        u2 = User(username="Morty", email="morty@c137.com", isVerified=1)
        u3 = User(username="Beth", email="beth@c137.com", isVerified=1)
        u4 = User(username="Rick", email ="iamgod@c134.com", isVerified=1)
        db.session.add_all([u1,u2,u3,u4])
        db.session.commit()

        #Add articles
        now = datetime.utcnow()
        a1 = Article(title="article 1", body="Article 1 Body", timestamp=now+timedelta(seconds=2), user_id=1, isSubmitted=True)
        a2 = Article(title="article 2", body="Article 2 Body", timestamp=now+timedelta(seconds=1), user_id=1, isSubmitted=True)
        a3 = Article(title="article 3", body="Article 3 Body", timestamp=now+timedelta(seconds=4), user_id=1, isSubmitted=True)
        a4 = Article(title="article 4", body="Article 3 Body", timestamp=now+timedelta(seconds=3), user_id=1, isSubmitted=True)
        a_draft1 = Article(title="Unsubmitted Post 1", body="Unsubmitted Body 1", timestamp=now+timedelta(seconds=2), user_id=1, isSubmitted = False)
        a_draft2 = Article(title="Unsubmitted Post 2", body="Unsubmitted Body 2", timestamp=now+timedelta(seconds=1), user_id=1, isSubmitted = False)
        
        db.session.add_all([a1,a2,a3,a4,a_draft1,a_draft2])
        db.session.commit()

        #test articles being fetched and the order of it. Also making sure draft articles don't show up
        blog = db.session.scalars(Article.fetch().order_by(Article.timestamp.desc())).all()
        assert blog == [a3, a4, a1, a2]

        #fetching draft articles
        draft_articles = db.session.scalars(Article.fetch_draft().order_by(Article.timestamp.desc())).all()
        assert draft_articles == [a_draft1, a_draft2]

        #add tags
        t1 = Tag(name="tag1")
        t2 = Tag(name="tag2")
        t3 = Tag(name="tag3")
        t4 = Tag(name="tag4")
        db.session.add_all([t1,t2,t3,t4])
        
        #associate tags to articles
        a1.tag(t1)
        a2.tag(t1)
        a3.tag(t1)

        a1.tag(t2)
        a2.tag(t2)

        a2.tag(t3)
        a3.tag(t3)
        
        a4.tag(t4)
        db.session.commit()

        #test articles given tag
        blog_Tag1 = db.session.scalars(t1.articles.select().order_by(Article.timestamp.desc())).all()
        blog_Tag2 = db.session.scalars(t2.articles.select().order_by(Article.timestamp.desc())).all()
        blog_Tag3 = db.session.scalars(t3.articles.select().order_by(Article.timestamp.desc())).all()
        blog_Tag4 = db.session.scalars(t4.articles.select().order_by(Article.timestamp.desc())).all()

        assert blog_Tag1 == [a3, a1, a2]
        assert blog_Tag2 == [a1, a2]
        assert blog_Tag3 == [a3, a2]
        assert blog_Tag4 == [a4]

        #Retrieve tags given an article
        count_articles_t1 = db.session.scalar(sa.select(sa.func.count()).select_from(
            t1.articles.select().subquery()))
        count_articles_t2 = db.session.scalar(sa.select(sa.func.count()).select_from(
            t2.articles.select().subquery()))
        count_articles_t3 = db.session.scalar(sa.select(sa.func.count()).select_from(
            t3.articles.select().subquery()))
        count_articles_t4 = db.session.scalar(sa.select(sa.func.count()).select_from(
            t4.articles.select().subquery()))
        
        assert count_articles_t1 == 3
        assert count_articles_t2 == 2
        assert count_articles_t3 == 2
        assert count_articles_t4 == 1

        #delete tags from articles
        a2.untag(t1)
        db.session.commit()
        assert t1.count_articles() == 2
        blog_Tag1 = db.session.scalars(t1.articles.select().order_by(Article.timestamp.desc())).all()
        assert blog_Tag1 == [a3, a1]

        #delete tags altogether (when a tag is deleted, the relationship has to be gone too)
        t2.delete()
        db.session.commit()
        a1_count_tags = db.session.scalar(sa.select(sa.func.count()).select_from(a1.tags.select().subquery()))
        a2_count_tags = db.session.scalar(sa.select(sa.func.count()).select_from(a2.tags.select().subquery()))

        #test article deletion removes tags with no more articles
        a4_id = a4.id
        a4.delete()
        db.session.commit()
        countT4 = db.session.scalar(sa.select(sa.func.count()).select_from(
            sa.select(Tag).filter_by(id=a4_id).subquery()))
        
        assert countT4 == 0

        assert a1_count_tags == 1
        assert a2_count_tags == 1
    
    def test_comments(self):
        #Add users
        u1 = User(username="Summer", email="summer@c137.com", isVerified=1)
        u2 = User(username="Morty", email="morty@c137.com", isVerified=1)
        u3 = User(username="Beth", email="beth@c137.com", isVerified=1)
        u4 = User(username="Rick", email ="iamgod@c134.com", isVerified=1)
        db.session.add_all([u1,u2,u3,u4])
        db.session.commit()

        #Add articles
        now = datetime.utcnow()
        a1 = Article(title="article 1", body="Article 1 Body", timestamp=now+timedelta(seconds=2), user_id=1, isSubmitted=True)
        a2 = Article(title="article 2", body="Article 2 Body", timestamp=now+timedelta(seconds=1), user_id=1, isSubmitted=True)
        a3 = Article(title="article 3", body="Article 3 Body", timestamp=now+timedelta(seconds=4), user_id=1, isSubmitted=True)
        a4 = Article(title="article 4", body="Article 4 Body", timestamp=now+timedelta(seconds=3), user_id=1, isSubmitted=True)
        db.session.add_all([a1,a2,a3,a4])
        db.session.commit()

        #test comment submission
        #article 1 comments
        a1c1 = Comment(comment="article1 comment1", user_id=2, article_id=1, timestamp = now+timedelta(seconds=3), isApproved=True)
        a1c2 = Comment(comment="article1 comment2", user_id=1, article_id=1, timestamp = now+timedelta(seconds=2), isApproved=True)
        a1c3 = Comment(comment="article1 comment3", user_id=2, article_id=1, timestamp = now+timedelta(seconds=1), isApproved=True)


        #article 2 comments
        a2c1 = Comment(comment="article2 comment1", user_id=2, article_id=2, timestamp = now+timedelta(seconds=1),isApproved=True)
        #to test pending comments don't show up
        a2c2 = Comment(comment="article2 comment2", user_id=2, article_id=2, timestamp = now+timedelta(seconds=2),isApproved=False)

        #article 3 comments
        a3c1 = Comment(comment="article3 comment1", user_id=3, article_id=3, isApproved=True)

        #article 4 comments
        a4c1 = Comment(comment="article4 comment1", user_id=4, article_id=4, isApproved=True)
        a4c2 = Comment(comment="article4 comment2", user_id=1, article_id=4, isApproved=True)

        db.session.add_all([a1c1, a1c2, a1c3, a2c1, a3c1, a4c1, a4c2])
        db.session.commit()

        #testing comment submissions    
        count_a1_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a1.fetch_approved_comments().subquery()))
        count_a2_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a2.fetch_approved_comments().subquery()))
        count_a3_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a3.fetch_approved_comments().subquery()))
        count_a4_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a4.fetch_approved_comments().subquery())) 
        
        assert count_a1_comments == 3
        assert count_a2_comments == 1
        assert count_a3_comments == 1
        assert count_a4_comments == 2

        #check that the oldest comment is displayed first
        a1_comments = db.session.scalars(a1.fetch_approved_comments().order_by(Comment.timestamp.asc())).all()
        assert a1_comments == [a1c3,a1c2,a1c1]
        
        #to test pending comments don't show up
        now = datetime.utcnow()
        a1c4 = Comment(comment="article1 comment4", user_id=2, article_id=1, timestamp = now+timedelta(seconds=1), isApproved=False)
        a2c2 = Comment(comment="article2 comment2", user_id=2, article_id=1, timestamp = now+timedelta(seconds=2), isApproved=False)
        db.session.add_all([a1c4, a2c2])
        db.session.commit()

        count_a1_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a1.fetch_approved_comments().subquery()))
        count_a2_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a2.fetch_approved_comments().subquery()))
        assert count_a1_comments == 3
        assert count_a2_comments == 1

        #test comment deletion
        a1c3.delete()
        count_a1_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
          a1.fetch_approved_comments().subquery()))
        assert count_a1_comments == 2
        
        #article deletion results in comment deletion
        a4_id = a4.id
        a4.delete()
        db.session.commit()
        count_a4_comments = db.session.scalar(sa.select(sa.func.count()).select_from(
            sa.select(Comment).filter_by(article_id = a4_id).subquery()))

        assert count_a4_comments == 0

        #fetch pending comments
        pending_comments = db.session.scalars(Comment.fetch_pending_approval_comments().order_by(Comment.timestamp.asc())).all()
        assert pending_comments == [a1c4, a2c2]
        

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
        u1 = User(username="Summer", email="summer@c137.com", isVerified=1)
        u2 = User(username="Morty", email="morty@c137.com", isVerified=1)
        u3 = User(username="Beth", email="beth@c137.com", isVerified=1)
        u4 = User(username="Rick", email ="iamgod@c134.com", isVerified=1)
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
