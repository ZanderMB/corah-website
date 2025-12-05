from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from CORAH.models import Event, Attendee
import pandas as pd

class Command(BaseCommand):
    help = 'Import data from separate CSV files for Monsters, Items, and Survivors'

    def handle(self, *args, **kwargs): #Paths to my data filses
        event_file_path = '/app/data-dump/eventfiller.csv'
        user_file_path = '/app/data-dump/userfiller.csv'

        # Import functions
        self.import_events(event_file_path)
        self.import_users(user_file_path)

        self.stdout.write(self.style.SUCCESS('\nAll data has been successfully imported.'))

    def import_events(self, file_path):
        """Imports Eventsa data from a given CSV file."""
        try:
            df = pd.read_csv(file_path)
            self.stdout.write(self.style.HTTP_INFO(f'Starting evenrt import from {file_path}...'))

            for _, row in df.iterrows():
                obj, created = Event.objects.get_or_create(
                    title=row['title'],
                    defaults={
                        'date': row['date'],
                        'location': row['location'],
                        'capacity': row['capacity'],
                        'seats_taken': row['seats_taken'],
                    }
                )
                if created:
                    self.stdout.write(f'  + Created Event: {obj.title}')
            
            self.stdout.write(self.style.SUCCESS('Event import complete.\n'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}. Skipping event import.'))
            
    def import_users(self, file_path):
        """
        Imports data into the Attendee table.
        Required: Creates the linked Django Auth User first.
        """
        try:
            df = pd.read_csv(file_path)
            self.stdout.write(self.style.HTTP_INFO(f'Starting Import from {file_path}...'))

            for _, row in df.iterrows():
                
                # STEP 1: Handle the Login Account (Django Auth User)
                # The 'username' column from CSV belongs here.
                user_account, created_account = User.objects.get_or_create(
                    username=row['username'], 
                    defaults={
                        'email': row['email'],
                        'first_name': row['name'].split()[0] if ' ' in row['name'] else row['name'],
                    }
                )

                if created_account:
                    user_account.set_password('CorahPass123!')
                    user_account.save()

                # STEP 2: Handle the Profile (Your 'Attendee' Model)
                # We link it to the account created above using 'user=user_account'.
                # We do NOT pass 'username' here, because Attendee doesn't have that field.
                attendee, created_profile = Attendee.objects.get_or_create(
                    user=user_account, 
                    defaults={
                        'name': row['name'],
                        'email': row['email'],
                    }
                )

                if created_profile:
                    self.stdout.write(f'  + Created Attendee: {attendee.name}')
                
            self.stdout.write(self.style.SUCCESS('Import complete.\n'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing: {e}'))