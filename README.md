# Project TweetPipe
*Start June 10th, 2019*

## Tasks:
 - Write a tool that accepts a twitter username X and a tweet count N as 
 parameters and fetches the last N tweets of user X.

 - Persist the data.
  
 - Check your code into Github and sent the link before you come onside

**Bonus:**
 - use an ORM
 - schema migrations
 - build any sql aggregate and display result after persisting


## Version 1
*June 12th, 2019*
See tag: [2019-06-12-v1](https://github.com/JimFawkes/tweetpipe/tree/2019-06-12-v1)

### Setup:
 1) Install requirements `pip install -r requirements/prod.txt` (*Run in appropriate ENV e.g., virtualenv*)
 1) Setup PostgrSQL DB
 1) Setup AWS S3 bucket
 1) Enter secrets in .env file (see [.example.env](tweetpipe/config/.example.env))
 1) Run DB migrations `python manage.py migrate`

### Run the application:
Process the last 10 tweets of [contentful](https://twitter.com/contentful).
```bash
$ python tweetpipe --user contentful --count 10
```
More Info can be found by running the following:
```bash
$ python tweetpipe --help

usage: tweetpipe [-h] [--user_handle USER_HANDLE] [--count COUNT] [--list]
                 [--rerun_file RERUN_FILE]

Project TweetPipe - A Contentful Challenge

Retrieve twitter data for a given username, transform the data
and store it in a DB.

The steps are:
    1) Get last 'count' tweets of user ('user_handle')
    2) Store the data along with metadata in an S3 Bucket
    3) Transform the raw data
    4) Store transformed data in the DB

In addition to the base process, it is also possible to list all files stored in S3 and to
re-run the pipeline using the data in S3 instead of newly fetched data.

optional arguments:
  -h, --help            show this help message and exit
  --user_handle USER_HANDLE, -u USER_HANDLE
                        twitter user handle (@'handle')
  --count COUNT, -c COUNT
                        nuber of recent tweets to retrieve
  --list, -l            list all retrieved files stored in S3 for a given
                        username
  --rerun_file RERUN_FILE
                        re-process and store data from a file stored in S3

Written as first draft by Moritz Eilfort.
```