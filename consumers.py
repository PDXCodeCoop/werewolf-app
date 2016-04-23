import re
import json
from channels import Group
from channels.sessions import channel_session
from django.db.models import Count
from models import Room, Game, Turn, Role, Player, Vote

from consumers_functions import *
from consumers_processing import *

import logging
log = logging.getLogger(__name__)

@channel_session
def ws_connect(message):
    try:
        url = message['path'].strip('/').split('/')
        label = url[-1]
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s',
        room.label, message['client'][0], message['client'][1])
    Group('vote-'+label).add(message.reply_channel)
    message.channel_session['room'] = room.label

    if 'roster' in url[-2]:
        game = room.games.latest('pk')
        players = getPlayers(game)
        Group('vote-'+label).send({'text': json.dumps({"players":players})})

@channel_session
def ws_receive(message):
    output = {}
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, but room does not exist label=%s', label)
        return

    #Initialize new data
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.error("ws message isn't json sentence=%s", message)
        return
    log.error(data)
    #Set all objects
    output = {}
    if 'new_player' in data:
        output['players'] = getPlayers(Game.objects.get(pk=data['game']))
    if 'assign' in data:
        output['assign'] = processRoles(data['game'])
    if 'voter' in data:
        output = process_vote(data)
    if 'new_game' in data:
        output['new_game'] = createNewGame(room, Game.objects.get(pk=data['game']))

    Group('vote-'+label).send({'text': json.dumps(output)})

@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label="test")
        Group('test').discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        log.error("room doesn't exist")
