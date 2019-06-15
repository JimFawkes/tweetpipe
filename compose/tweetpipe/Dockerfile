FROM python:3.7.3
LABEL author="Moritz Eilfort"

WORKDIR /app/tweetpipe
COPY requirements requirements
RUN pip install -r requirements/prod.txt

COPY tweetpipe tweetpipe

ENTRYPOINT [ "python", "tweetpipe" ]
CMD ["--help"]


