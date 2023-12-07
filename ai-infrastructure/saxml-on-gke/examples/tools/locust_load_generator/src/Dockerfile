FROM locustio/locust

RUN pip install -U pip 
RUN pip install jsonlines google-cloud-pubsub google-cloud-storage transformers sentencepiece 

WORKDIR /app
COPY . .

