# Flask-Microblog

## Installation:
1. Clone the repo via `git clone https://github.com/learningCJ/Flask-Microblog`
2. Create virtual environment by `python venv venv`
3. (Optional)To enable search, please download ElasticSearch from [here](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/installation.html)
4. Create a .env file and set the following information to have email, translation, and search capabilities:
   1. Email Related (Required for account registration):
      1. SENDGRID_API_KEY="Your SendGrid API Key"
      2. MAIL_DEFAULT_SENDER="\<your email\>"
      3. MAIL_ERROR_SENDER="\<your email address (can be the same as above)\>"
   3. Translation Related(Required for Translation capability):
      1. MS_TRANSLATOR_KEY="\<Your Microsoft API Key\>"
   4. Elasticsearch(Required for Search functionality):
      1. ELASTICSEARCH_URL=\<ElasticSearch URL\> (leave this blank if you don't 
      2. ELASTICSEARCH_PW="\<Your ElasticSearch Password provided\>"
      3. ELASTICSEARCH_CERT_DIR="/path/to/elasticsearch/certificate" (This certificate comes with the installation of ElasticSearch)
      4. ELASTICSEARCH_USERNAME = 'elastic' (note: By version 8.8, the username is "elastic", but might differ based on versions)
5. Install all dependencies by `pip install -r requirements.txt` 
