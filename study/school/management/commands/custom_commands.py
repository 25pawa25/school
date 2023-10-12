from django.core.management import BaseCommand

from school.models import CustomUser


class Command(BaseCommand):
    help = 'Create random users'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--admin', action='store_true', help='Создание учетной записи администратора')

    def handle(self, *args, **kwargs):
        admin = kwargs['admin']

        first_name = 'pavel'
        last_name = 'polunin'
        phone = '89026971190'
        password = '12345'
        CustomUser.objects.create_superuser(phone=phone, first_name=first_name, password=password, last_name=last_name)

