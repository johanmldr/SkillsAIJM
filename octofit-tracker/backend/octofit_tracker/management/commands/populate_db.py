from django.core.management.base import BaseCommand
from octofit_tracker.models import User, Team, Activity, Leaderboard, Workout
from django.conf import settings
from pymongo import MongoClient
from datetime import timedelta
from bson import ObjectId
from octofit_tracker.test_data import test_users, test_teams, test_activities, test_leaderboard, test_workouts

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activity, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['PORT'])
        db = client[settings.DATABASES['default']['NAME']]

        # Drop existing collections
        db.users.drop()
        db.teams.drop()
        db.activity.drop()
        db.leaderboard.drop()
        db.workouts.drop()

        # Populate users
        users = [User(_id=ObjectId(), **user) for user in test_users]
        User.objects.bulk_create(users)

        # Populate teams
        for team_data in test_teams:
            team = Team(_id=ObjectId(), name=team_data['name'])
            team.save()
            team.members.add(*users)

        # Populate activities
        activities = [
            Activity(
                _id=ObjectId(),
                user=User.objects.get(username=activity['username']),
                activity_type=activity['activity_type'],
                duration=timedelta(hours=int(activity['duration'].split(':')[0]), minutes=int(activity['duration'].split(':')[1]))
            )
            for activity in test_activities
        ]
        Activity.objects.bulk_create(activities)

        # Populate leaderboard
        leaderboard_entries = [
            Leaderboard(
                _id=ObjectId(),
                user=User.objects.get(username=entry['username']),
                score=entry['score']
            )
            for entry in test_leaderboard
        ]
        Leaderboard.objects.bulk_create(leaderboard_entries)

        # Populate workouts
        workouts = [Workout(_id=ObjectId(), **workout) for workout in test_workouts]
        Workout.objects.bulk_create(workouts)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
