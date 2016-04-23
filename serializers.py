from django.forms import widgets
from rest_framework import serializers
from django.contrib.auth.models import User
from models import *

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ('pk', 'name', 'label', 'games')

class VoteSerializer(serializers.HyperlinkedModelSerializer):
    voter = serializers.PrimaryKeyRelatedField(read_only=True)
    target = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Vote
        fields = ('pk', 'turn', 'voter', 'target', 'category')

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('pk', 'name', 'label', 'description', 'description_abilities')

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    role = RoleSerializer()
    class Meta:
        model = Player
        fields = ('pk', 'name', 'game', 'role', 'turn')

class TurnSerializer(serializers.HyperlinkedModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    votes = VoteSerializer(read_only=True, many=True)
    class Meta:
        model = Turn
        fields = ('pk', 'game', 'counter', 'players', 'votes', 'winner')

class GameSerializer(serializers.HyperlinkedModelSerializer):
    turns = TurnSerializer(many=True)
    class Meta:
        model = Game
        fields = ('pk', 'room', 'players', 'turns')
