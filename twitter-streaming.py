#https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Sampled-Stream/sampled-stream.py

import requests
import os
import json
import boto3
import random
import time
import tweepy 

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
#bearer_token = os.environ.get("BEARER_TOKEN")
consumer_key = "fGFOmQId24tRKmtsIpoD4nntd"
consumer_secret = "ntRsegY8alhDcXdFN0aaco3sG5lAMi5Vx8eYnwKgybpWZffl3f"
access_token = "1467680913081331713-BRiiOvb54UtmHUmYPVPSGCWkZJQKl5"
access_token_secret = "0fOOgFC05CwchbRwraf6v7NfX9Ns1cr2QYJw56nakVEe9"
bearer_token= "AAAAAAAAAAAAAAAAAAAAABpTWgEAAAAA2IhEST15Cg31Y4%2FtgqM0%2FL2diik%3DKSwKw1OuXdRzJUzpF7T3DdRymD2JIT2yrUNl7dwuxfdahJQ38R" 

streamName = 'PUT-S3-qFeoj'

url = "https://api.twitter.com/2/tweets/search/stream?tweet.fields=author_id,attachments&user.fields=name&expansions=author_id"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value" : "feeling lang:en is:verified"}
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))



def get_stream(set):
    response = requests.get(url, auth=bearer_oauth, stream=True)
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            response = kinesis_client.put_record_batch(
                DeliveryStreamName=streamName,
                Records=[
                    {
                       "Data" :  response_line
                        }
                    ]
                )
            #print(response)
            #print(json.dumps(json_response, indent=4, sort_keys=True))

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)

if __name__ == "__main__":
    kinesis_client = boto3.client('firehose', region_name = 'us-east-1')
    main()