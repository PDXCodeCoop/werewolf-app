from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=20)
    label = models.SlugField(unique=True)
    testing = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    def __unicode__(self):
        return self.label
    def as_dict(self):
        return {'pk':self.pk, 'name': self.name, 'label': self.label}

class Game(models.Model):
    room = models.ForeignKey(Room, related_name='games')
    counter = models.IntegerField(default = 1)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    assigned = models.BooleanField(default=False)
    winner = models.CharField(max_length=50, null=True, blank=True)
    def __unicode__(self):
        return "Room %s: Game #%s, %s turns" % (self.room.label, self.pk, self.turns.count())
    def as_dict(self):
        output = {'pk':self.pk, 'room': self.room.label}
        return output

class Turn(models.Model):
    game = models.ForeignKey(Game, related_name='turns')
    counter = models.IntegerField(default = 1)
    winner = models.CharField(max_length=50, null=True, blank=True)
    def __unicode__(self):
        return "game %s, turn:%s" % (self.game.pk, self.counter)
    def as_dict(self):
        return {'counter': self.counter}

class Role(models.Model):
    name = models.CharField(max_length=140)
    label = models.SlugField(unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    description_abilities = models.TextField(max_length=500, blank=True, null=True)
    def __unicode__(self):
        return self.label
    def as_dict(self):
        return {'pk': self.pk, 'name': self.name, 'label': self.label}

class Player(models.Model):
    name = models.CharField(max_length=140)
    game = models.ForeignKey(Game, related_name='players')
    turn = models.ManyToManyField(Turn, related_name='players')
    role = models.ForeignKey(Role, related_name='players', null=True, blank=True)
    def __unicode__(self):
        return "%s" % (self.name)
    def as_dict(self):
        output = {'pk': self.pk, 'name': self.name, 'game': self.game.pk}
        if self.role is not None:
            output['role'] = self.role.as_dict()
        return output

class Vote(models.Model):
    turn = models.ForeignKey(Turn, related_name='votes')
    voter = models.ForeignKey(Player, related_name='votes', null=True, blank=True)
    target = models.ForeignKey(Player, related_name='targets', null=True, blank=True)
    category = models.CharField(max_length=140, default='player')
    def __unicode__(self):
        return "%s) %s -> %s" %(self.turn, self.voter.name, self.target.name)
    def as_dict(self):
        return {
                'voter':self.voter.name, 'voter_pk':self.voter.pk,
                'target':self.target.name, 'target_pk':self.target.pk}
