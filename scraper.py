from instagram.client import InstagramAPI
from alchemyapi import AlchemyAPI
from datetime import datetime, timedelta
import math

api = InstagramAPI(client_id='64de641b01d648779939696d77ccff38', client_secret='043233db9a2c4c13a40a442c7bee0c43')
alchemyapi = AlchemyAPI()

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
    #   user
    #   created time
    return {
        'type': media.type,
        'thumbnail': media.get_thumbnail_url(),
        'link': media.get_standard_resolution_url(),
        'caption': media.caption.text,
        'like_count': media.like_count,
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

def getUserInfluence(user):
    # returns user influence score based on this formula:
    # sqrt(user_posts) * (user_followers / user_following) * math.log(user_followers+1, 2)
    userInfo = fetchUserInfo(user)
    return math.sqrt(userInfo['posts']) * (userInfo['followers']/float(userInfo['following'])) * math.log(userInfo['followers']+1, 2)

def analyzeSentiment(media):
    # uses AlchemyAPI's sentiment analysis to parse sentiment into a raw score
    # prepend string with a period (.) if first character is a hash (#)
    sentiment = alchemyapi.sentiment('text', media['caption'])
    if sentiment['status'] != 'OK':
        raise Exception(sentiment['statusInfo'])
    try:
        return (float(sentiment['docSentiment']['score']), sentiment['docSentiment']['type'])
    except KeyError:
        return (0.0, 'neutral')

def calculateScore(media):
    user = media['user']
    influence = getUserInfluence(user)
    try:
        sentiment, type_ = analyzeSentiment(media)
    except Exception, e:
        print "Error getting sentiment:", e
        sentiment, type_ = 0.0, 'neutral'
    return {
        'score': influence * sentiment,
        'type': type_
    }

capitalonemedia = fetchLatestMedia("CapitalOne", 7)
capitalone = map(fetchMediaInfo, capitalonemedia)
print "Calculating scores"
for media in capitalone:
    print media['caption']
    print calculateScore(media)
    print
