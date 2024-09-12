from pytwitter import Api
from datetime import datetime, timedelta

api = Api(bearer_token="Your bearer token")

class XClient:
    def __init__(self, client_id: str, client_secret: str, access_token: str):
        self.api = Api(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
        )
        

    def get_tweets_past_hour(self):
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        one_hour_ago_str = one_hour_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        tweets = self.api.search_tweets(query="*", start_time=one_hour_ago_str)
        return tweets