from instagram.client import InstagramAPI
#from alchemyapi import AlchemyAPI
from datetime import datetime, timedelta

api = InstagramAPI(client_id='64de641b01d648779939696d77ccff38', client_secret='043233db9a2c4c13a40a442c7bee0c43')
#alchemyapi = AlchemyAPI()

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
            break
    print "Returning", len(media), "items with tag", tag_name
    return media

def fetchMediaInfo(media):
    # fetch these info from each media:
    #   type
    #   thumbnail URL
    #   high-res URL
    #   caption text
    #   num likes
    #   comments
    #   user
    #   created time
    return {
        'type': media.type,
        'thumbnail': media.get_thumbnail_url(),
        'link': media.get_standard_resolution_url(),
        'caption': media.caption.text,
        'like_count': media.like_count,
        'comments': media.comments,
        'user': media.user,
        'created_time': media.created_time
    }

def countUserPosts(user):
    # user - user object
    # returns the number of posts the user has made
    media, next_ = api.user_recent_media(user_id=user.id, count=100)
    count = len(media)
    while next_:
        more_media, next_ = api.user_recent_media(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_media)
    return count

def countUserFollowers(user):
    # user - user object
    # returns the number of followers a user has
    followers, next_ = api.user_followed_by(user_id=user.id, count=100)
    count = len(followers)
    while next_:
        more_followers, next_ = api.user_followed_by(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_followers)
    return count

def countUserFollowing(user):
    # user -  user object
    # returns the number of people the user is following
    following, next_ = api.user_follows(user_id=user.id, count=100)
    count = len(following)
    while next_:
        more_following, next_ = api.user_follows(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_following)
    return count

def fetchUserInfo(user):
    # fetch these info from each user:
    #   num posts
    #   num followers
    #   num following
    return {
        'posts': countUserPosts(user),
        'followers': countUserFollowers(user),
        'following': countUserFollowing(user)
    }

def analyzeSentiment(media):
    # uses AlchemyAPI's sentiment analysis to parse sentiment into a raw score
    # prepend string with a period (.) if first character is a hash (#)
    comments = map(lambda comment: comment.text, media['comments'])
    pass # TODO

capitalonemedia = fetchLatestMedia("CapitalOne", 7)
capitalone = map(fetchMediaInfo, capitalonemedia)
