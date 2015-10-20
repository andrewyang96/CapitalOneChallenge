from instagram.client import InstagramAPI
from datetime import datetime, timedelta
api = InstagramAPI(client_id='64de641b01d648779939696d77ccff38', client_secret='043233db9a2c4c13a40a442c7bee0c43')

def fetchLatestMedia(tag_name, max_age=7):
    # tag_name - the hashtag name
    # max_age - oldest returned Media object in days
    # returns a list of Media objects
    media, next_ = api.tag_recent_media(tag_name=tag_name, count=100)
    oldest_dt = datetime.now() - timedelta(days=max_age)
    while next_:
        more_media, next_ = api.tag_recent_media(tag_name=tag_name, count=100, with_next_url=next_)
        filtered = filter(lambda media: media.created_time > oldest_dt, more_media)
        media.extend(filtered)
        if len(filtered) != len(more_media):
            return media
    return media

# Fetch 20 most recent posts with #CapitalOne tag
capitalone = fetchLatestMedia("capitalone", 7)
