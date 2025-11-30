from django.core.management.base import BaseCommand
from users.models import Users

class Command(BaseCommand):
    help = 'Set passwords for existing users'

    def handle(self, *args, **options):
        users = Users.objects.all()
        for user in users:
            user.set_password('password321')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Password set for {user.email}')
            )