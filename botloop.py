from picamera import PiCamera
from datetime import datetime, timedelta
from time import sleep
import schedule
import tweepy
import config

camera = PiCamera()
camera.resolution = (1920, 1080)

# Function that triggers with mentions
def trigger():

    # Twitter authentication
    client = tweepy.Client(config.BEARER_TOKEN, config.API_KEY,config.API_SECRET, config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    auth = tweepy.OAuth1UserHandler(config.API_KEY, config.API_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # Get user mentions and set the start id to the first mention's id.
    client_id = client.get_me().data.id
    start_id = 0
    mentions = client.get_users_mentions(client_id)
    if mentions.data != None:
        start_id = mentions.data[0].id

    # Words that will trigger the function if they are included in the mention.
    triggers = ["!Capture", "!capture", "Capture!", "capture!"]

    startTime = datetime.now()
    endTime = startTime + timedelta(minutes=10)
    print('S: ' + str(datetime.now()))

    # Loop that keeps checking for new mentions
    while datetime.now() < endTime:

        response = client.get_users_mentions(client_id, since_id=start_id, expansions='author_id')

        if response.data != None:
            for mention in response.data:
                if int(mention.author_id) != client_id:
                    if True in [trigger in mention.text.lower() for trigger in triggers]:
                        try:
                            user = api.get_user(user_id=mention.author_id)
                            print(f'@{user.screen_name} triggered a capture: {mention.text}')

                            now = datetime.now()
                            filename = "{0:%d}{0:%m}{0:%y}-{0:%H}{0:%M}.png".format(now)
                            date = "{0:%H}:{0:%M}, {0:%A}, {0:%B} {0:%e}, {0:%Y}".format(now)

                            camera.annotate_text = f'Captured triggered by @{user.screen_name} at {date}'
                            camera.capture("/home/pi/twitterbot/captures/{0}".format(filename))
                            camera.close

                            status = f'Here you go. Picture 📸 taken at {date}.'
                            picture = f'/home/pi/twitterbot/captures/{filename}'

                            media = api.media_upload(picture)
                            client.create_tweet(in_reply_to_tweet_id=mention.id, text=status, media_ids=[media.media_id])

                            start_id = mention .id

                        except Exception as error:
                            print(error)
                            camera.close
            time.sleep(5)


# Function that triggers by schedule
def daily():
        
    # Twitter authentication
    client = tweepy.Client(config.BEARER_TOKEN, config.API_KEY,config.API_SECRET, config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    auth = tweepy.OAuth1UserHandler(config.API_KEY, config.API_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    now = datetime.now()
    filename = "{0:%d}{0:%m}{0:%y}-{0:%H}{0:%M}.jpg".format(now)
    date = "{0:%H}:{0:%M}, {0:%A}, {0:%B} {0:%e}, {0:%Y}".format(now)

    camera.capture("/home/pi/twitterbot/captures/{0}".format(filename))
    camera.close

    status = f'Picture taken at {date}'
    picture = f'/home/pi/twitterbot/captures/{filename}'

    media = api.media_upload(picture)
    client.create_tweet(text=status, media_ids=[media.media_id])

# Scheduling of the functions so that we can run both throughout the day.
schedule.every().day.at("08:00").do(daily)
schedule.every().day.at("08:02").do(trigger)
schedule.every().day.at("11:00").do(daily)
schedule.every().day.at("11:02").do(trigger)
schedule.every().day.at("14:00").do(daily)
schedule.every().day.at("14:02").do(trigger)
schedule.every().day.at("17:00").do(daily)
