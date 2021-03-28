# Listeners
Checks various services every so often and posts things.

Has no new dependencies.

## Steam
Checks Steam announcements for the game IDs given, and posts them in the given channel.


## Twich
Checks Twitch streamers and posts when they are online or offline in the given channel.

### Setup
1. Log into the [Twitch Developer Console](https://dev.twitch.tv/console/apps)
1. Register Application
1. Give a decent name, set the OAuth Redirect URL to `https://localhost`, select the Category `Application Integration`
1. Check the I'm not a robot, press Create.
1. Open up `data/cache/twitch_config.yaml`, if it's not there then run the bot while having the Listener Module active.
1. Put the Client ID and Client Secret from the webpage into the config.

