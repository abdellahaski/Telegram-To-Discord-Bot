# Telegram-To-Discord
Forward message from the specified Telegram channel to Discord Webhooks with all the media

### Requirements
1. Python 3.6+ 
2. Telegram APPID and HASH (can be created from here https://core.telegram.org/api/obtaining_api_id)
3. Have a Telegram account with valid phone number
4. Discord webhooks for the channels you to forward to

### Installing and Setup

1. Clone this repository `git clone https://github.com/abdellahaski/Telegram-To-Discord-Bot.git`.
2. Open your choice of console (or Anaconda console) and navigate to cloned folder  `cd Telegram-To-Discord-Bot.git`.
3. Run Command: `pip3 install -r requirements.txt`.
4. Rename `example.env` and `example.config.json5` to `.env` and `config.json5` respectively 
5. Fill out the .env and config.json5 files
6. Run the bot by this command: `python3 main.py`

#### Filling `.env` file
* Add your Telegram `api_id` and `api_hash` to the `.env` file | Read more [here](https://core.telegram.org/api/obtaining_api_id)
* Specify an existing temporary directory to the `DLLOC` variable (e.g.: C:/tmp or /tmp)
* Specify the text to append to each of the forwarded messages in the `TEXT_TO_PREPEND` variable (it can be a ping (`@everyone`, `@here`, or `@role`) and it can be a text or emojies like `:point_right:`)


#### Filling `config.json5` file
The ``config.json5` file contains a JSON array (list) of Telegram channel you want to forward messages from all along with specific configuration for each TG channel:

* `TGchannelID` : Telegram ID of the channel that you want to forward from (you can get it by forwarding any message from that channel to [@jsondumpbot](https://t.me/jsondumpbot)) don't forget to remove the first part (-100) from the ID
* `senderAvatarUrl` : The avatar URL that will be shown on Discord sender profile (if it's empty it will be pulled automatically from the Telegram channel profile picture)
* `senderName` : The sender name that will be shown on Discord sender profile (if it's empty it will default to the Telegram channel name)
* `DiscordWebhooks` : Contains a list of the Discord webhooks that you want messages to be forwarded to
```
You can have as many TG channels as you want forwarding message to as many as Discord webhooks you want
```
