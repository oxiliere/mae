import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext as _
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default admin user for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=getattr(settings, 'DEFAULT_ADMIN_EMAIL', 'admin@oxiliere.com'),
            help=f'Email address for the admin user (default: {getattr(settings, "DEFAULT_ADMIN_EMAIL", "admin@oxiliere.com")})'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user (if not provided, will use environment variable ADMIN_PASSWORD or prompt)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name for the admin user (default: Admin)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the admin user (default: User)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user already exists (will update existing user)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        force = options['force']

        # Get password from environment variable if not provided
        if not password:
            password = os.environ.get('ADMIN_PASSWORD') or getattr(settings, 'DEFAULT_ADMIN_PWD', None)
            if not password:
                password = input('Enter password for admin user: ')

        if not password:
            raise CommandError('Password is required')

        try:
            with transaction.atomic():
                # Check if user already exists
                user_exists = User.objects.filter(email=email).exists()
                
                if user_exists and not force:
                    raise CommandError(
                        f'User with email {email} already exists. Use --force to update existing user.'
                    )
                
                if user_exists and force:
                    # Update existing user
                    user = User.objects.get(email=email)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.set_password(password)
                    user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully updated admin user: {email}'
                        )
                    )
                else:
                    # Create new user
                    user = User.objects.create_superuser(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created admin user: {email}'
                        )
                    )

                # Display user information
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f'Admin user details:\n'
                        f'  Email: {user.email}\n'
                        f'  Name: {user.get_full_name()}\n'
                        f'  Staff: {user.is_staff}\n'
                        f'  Superuser: {user.is_superuser}\n'
                        f'  Active: {user.is_active}'
                    )
                )

        except Exception as e:
            raise CommandError(f'Error creating admin user: {str(e)}')
