# Flask-Microblog

## Features:
1. **Uses Flask-Migrate to migrate/upgrade database schemas** 
2. **User features:**
   *    Registration with password encryption using Werkzeug 
   *    Login using Flask-Login
   *    Email confirmation and password reset using Json Web Token (JWT) and email sending done with SendGrid
   *    Ability to follow users and the posts from users they follow displayed on their home page
   *    User profile (user.html):
        *    Edit About Me
        *    Last login date and time
        *    List of all posts with the ability to delete them complete with bootstrap modal
        *    Resend email confirmation in case registration confirmation expires
        *    Delete posts
        *    Pagination
        *    See other user’s profile page (uses the same html template as own profile)
        *    Unfollow the page owner
   *    Home (index.html)
        *    Submit your post only if your email is verified
        *    Unfollow author of a post
        *    Delete your own post
        *    Pagination
   *    Explore page (using the same template as the main feed)
        *    Follow/unfollow users
        *    Delete own post
        *    Pagination
   *    Registration
        *    Showing the password requirements being met on a case by case basis using Javascript
        *    Validations to ensure that the required information is provided and ensuring no duplication in username and email with another user
3. **Site wide features:**
   *    Navbar styled using Bootstrap navbar
   *    Ability to search the sitewide posts using ElasticSearch
   *    Localized the site for Korean users - automatically detect based on system + browser using Flask Babel
   *    Translation services if the post language is different than the user’s locale using jQuery and Javascript with a call made to Microsoft Azure Translation Services API
   *    Using blueprints to make the website scalable and portable
