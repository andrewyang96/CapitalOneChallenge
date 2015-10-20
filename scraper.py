from instagram.client import InstagramAPI
api = InstagramAPI(client_id='64de641b01d648779939696d77ccff38', client_secret='043233db9a2c4c13a40a442c7bee0c43')

def fetchLatestMedia(tag_name):
    media, next_ = api.tag_recent_media(tag_name="chillindude")
    while next_:
        more_media, next_ = api.tag_recent_media(tag_name=tag_name,with_next_url=next_)
        print "Next url:", next_
        media.extend(more_media)
    return media

# Fetch 20 most recent posts with #CapitalOne tag
capitalone = fetchLatestMedia("capitalone")
