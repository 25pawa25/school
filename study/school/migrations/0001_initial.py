# Generated by Django 4.1.3 on 2023-09-13 08:24

import ckeditor_uploader.fields
import dirtyfields.dirtyfields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_s3_storage.storage
import phonenumber_field.modelfields
import school.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=255, verbose_name='Фамилия')),
                ('patronymic', models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество')),
                ('description', models.CharField(blank=True, default='', max_length=600, null=True, verbose_name='Описание')),
                ('picture', models.ImageField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/teacher', verbose_name='Аватарка')),
                ('user_type', models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher')], default='student', max_length=255, verbose_name='Преподаватель/студент')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='RU', unique=True, verbose_name='Телефон')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('password', models.CharField(max_length=5, unique=True, verbose_name='Проверочный код')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', school.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название новости')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Текст новости')),
                ('description', models.CharField(default='', max_length=300, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/advertisement/image/', verbose_name='Картинка')),
                ('slug', models.SlugField(blank=True, help_text='Ссылка на blog: site.ru/advertise/[slug]. Заполняется автоматически', unique=True, verbose_name='Слаг новости')),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
            },
        ),
        migrations.CreateModel(
            name='Aim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=600, verbose_name='Цель')),
            ],
            options={
                'verbose_name': 'Цель',
                'verbose_name_plural': 'Цели',
            },
        ),
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(default='', max_length=255, verbose_name='Ответ')),
                ('right', models.BooleanField(default=False, verbose_name='Верный')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, help_text='Ссылка на ЛК: site.ru/courses/[slug]. Заполняется автоматически', unique=True, verbose_name='Слаг курса')),
                ('intro', models.ImageField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/course/intro/', verbose_name='Обложка')),
                ('description', models.CharField(default='', max_length=600, verbose_name='Описание')),
                ('tg_link', models.URLField(default='', verbose_name='Ссылка на ТГ канал')),
                ('cost', models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True)),
                ('paid', models.BooleanField(default=True, verbose_name='Платный курс')),
                ('aim', models.ManyToManyField(blank=True, related_name='aim', to='school.aim')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(blank=True, max_length=255, null=True, verbose_name='ФИО')),
                ('text', models.TextField(blank=True, null=True, verbose_name='Текст отзыва')),
                ('link', models.URLField(blank=True, default='', null=True, verbose_name='Ссылка')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='RU', verbose_name='Телефон')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('is_processed', models.BooleanField(default=False, verbose_name='Обработано')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=20, verbose_name='Класс')),
            ],
            options={
                'verbose_name': 'Класс',
                'verbose_name_plural': 'Классы',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', verbose_name='Формулировка задания')),
                ('latex_text', models.JSONField(blank=True, null=True, verbose_name='Латех')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=150, verbose_name='Заголовок сайта')),
                ('description', models.TextField(blank=True, help_text='Используется в meta description', max_length=150, verbose_name='Описание сайта')),
                ('phone', models.CharField(blank=True, default='', max_length=150, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='Электронная почта')),
                ('telegram', models.URLField(blank=True, default='', verbose_name='Телеграм')),
                ('instagram', models.URLField(blank=True, default='', verbose_name='Инстаграм')),
                ('facebook', models.URLField(blank=True, default='', verbose_name='Фейсбук')),
                ('youtube', models.URLField(blank=True, default='', verbose_name='Ютуб')),
                ('whatsapp', models.URLField(blank=True, default='', verbose_name='Вотсап')),
            ],
            options={
                'verbose_name': 'настройки сайта',
                'verbose_name_plural': 'настройки сайта',
            },
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=600, verbose_name='Предмет')),
            ],
            options={
                'verbose_name': 'Предмет',
                'verbose_name_plural': 'Предметы',
            },
        ),
        migrations.CreateModel(
            name='UserQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_question', models.TextField(verbose_name='Текст вопроса')),
                ('text_answer', models.TextField(blank=True, null=True, verbose_name='Текст ответа')),
                ('name', models.CharField(max_length=255, verbose_name='Имя')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='RU', verbose_name='Телефон')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Webinar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата вебинара')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webinar', to='school.course')),
            ],
            options={
                'verbose_name': 'Вебинар',
                'verbose_name_plural': 'Вебинары',
            },
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Номер лекции')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('video', models.FileField(storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/course/video', verbose_name='Видео')),
                ('short_video', models.FileField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/course/video', verbose_name='Короткое видео')),
                ('intro', models.ImageField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/course/video/intro', verbose_name='Превью')),
                ('slug', models.SlugField(blank=True, help_text='Ссылка на курс: site.ru/courses/[slug]. Заполняется автоматически', unique=True, verbose_name='Слаг видео')),
                ('description', models.CharField(default='', max_length=600, verbose_name='Описание видео')),
                ('start_time', models.DecimalField(decimal_places=0, default=1, max_digits=5, verbose_name='Начальная секунда обрезания видео')),
                ('end_time', models.DecimalField(decimal_places=0, default=180, max_digits=5, verbose_name='Конечная секунда обрезания видео')),
                ('course', models.ForeignKey(max_length=255, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='school.course')),
            ],
            options={
                'verbose_name': 'Видео',
                'verbose_name_plural': 'Видео',
            },
        ),
        migrations.CreateModel(
            name='UsersActiveVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False, verbose_name='Активно')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_active', to='school.videos')),
            ],
            options={
                'verbose_name': 'Активное видео пользователя',
                'verbose_name_plural': 'Активные видео пользователя',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school.answers')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answer', to='school.questions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Результат теста',
                'verbose_name_plural': 'Результаты тестов',
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/test/', verbose_name='Разбор теста')),
                ('video', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='school.videos')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='StudentWebinar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('webinar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_webinar', to='school.webinar')),
            ],
            options={
                'verbose_name': 'Вебинары студентов',
                'verbose_name_plural': 'Вебинары студентов',
            },
        ),
        migrations.AddField(
            model_name='questions',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='school.test'),
        ),
        migrations.CreateModel(
            name='PaidForCourse',
            fields=[
                ('order_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_status', models.BooleanField(default=False, verbose_name='Платеж выполнен')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paid_for_course', to='school.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Оплата курса',
                'verbose_name_plural': 'Оплата курса',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата сообщения')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'ordering': ['pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('file', models.FileField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/homework/', verbose_name='Домашнее задание')),
                ('teacher', models.ForeignKey(max_length=255, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='homework', to='school.videos')),
            ],
            options={
                'verbose_name': 'Домашнее задание',
                'verbose_name_plural': 'Домашнее задание',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='form',
            field=models.ManyToManyField(blank=True, related_name='form', to='school.form'),
        ),
        migrations.AddField(
            model_name='course',
            name='student',
            field=models.ManyToManyField(blank=True, max_length=255, related_name='student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='study',
            field=models.ManyToManyField(blank=True, related_name='study', to='school.study'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(blank=True, max_length=255, on_delete=django.db.models.deletion.PROTECT, related_name='teacher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CountCompletedTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Кол-во')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='count_unsuccess_test', to='school.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Кол-во неправильных тестов пользователей',
                'verbose_name_plural': 'Кол-во неправильных тестов пользователей',
            },
        ),
        migrations.CreateModel(
            name='CompletedTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(blank=True, max_length=25, null=True, verbose_name='Результат')),
                ('completed_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата прохождения')),
                ('success', models.BooleanField(default=False, verbose_name='Пройден успешно')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_test', to='school.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Тесты пользователей',
                'verbose_name_plural': 'Тесты пользователей',
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='kurs.stern.xyz', aws_s3_endpoint_url='https://hb.bizmrg.com'), upload_to='media/certificate/', verbose_name='Сертификат')),
                ('finished_course', models.BooleanField(default=False, verbose_name='Курс закончен')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate', to='school.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сертификат',
                'verbose_name_plural': 'Сертификаты',
            },
        ),
        migrations.AddField(
            model_name='answers',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='school.questions'),
        ),
        migrations.CreateModel(
            name='AnswerMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Сообщение')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата сообщения')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answer', to='school.message')),
            ],
            options={
                'verbose_name': 'Ответы на сообщения',
                'verbose_name_plural': 'Ответы на сообщения',
                'ordering': ['pub_date'],
            },
        ),
    ]
