from slack import WebClient
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import pandas as pd



weekmood = pd.read_csv('weekmood.csv')
count = pd.read_csv('count.csv')
print(count)


load_dotenv()

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

client = WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

message_counts = {}


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id :
        if user_id in message_counts:
            message_counts[user_id] += 1
        else: 
            message_counts[user_id] = 1
        

@app.route('/marche', methods = ['POST'])
def marche():
    data = request.form
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel= channel_id, 
    text= f"{user_name.capitalize()} a envie d'aller marcher ! Qui est partant.e pour l'accompagner ? "
    )
    return Response(), 200

@app.route('/weekmood', methods = ['POST'])
def week_mood():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    index = count.iat[0, 0]
    if count.iat[0, 0] >= len(weekmood) - 1:
        count.iat[0, 0] = 0
    else: 
        count.iat[0, 0]+= 1   
    count.to_csv("count.csv", index=False)
    client.chat_postMessage(channel= channel_id, 
    text= "Hello l'équipe :heart:" + 
        '\n\n' + 
        "_Vous trouverez ci-dessous l'organisation de notre point de jeudi matin :_"
        '\n\n' +
        "---------- Pour notre Week-mood : ----------" +"\n\n" +
        f"*{weekmood.at[index, 'Nom']} *" +
        '\n\n' +
        f" Pour t'aider :{ weekmood.at[index, 'link'] if weekmood.at[index, 'link'] == weekmood.at[index, 'link'] else ' pas de lien, désolé !' }"
        + '\n\n' + 
        f">Description : {weekmood.at[index, 'desc'] if weekmood.at[index, 'desc'] == weekmood.at[index, 'desc'] else 'Aucune. ' }"
    )
    return Response(), 200



if __name__ == "__main__":
    app.run(port = 3000, debug=True)