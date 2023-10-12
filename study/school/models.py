import json
import re
import time
import uuid

from dirtyfields import DirtyFieldsMixin

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models
from django_s3_storage.storage import S3Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from study.settings import SMS_SENDER_API_KEY, SMS_SENDER_NAME, SECURE, \
    AWS_S3_BUCKET_NAME, AWS_S3_ENDPOINT_URL

from .utils import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from random import randint as rnd
from django.urls import reverse_lazy
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
import random

USER_ROLES = (('student', "Student"), ('teacher', "Teacher"))

storage = S3Storage(aws_s3_bucket_name=AWS_S3_BUCKET_NAME,
                    aws_s3_endpoint_url=AWS_S3_ENDPOINT_URL)


def generate_password():
    numbers_list = [x for x in range(10)]
    code_items = []
    for i in range(5):
        num = random.choice(numbers_list)
        code_items.append(num)
    code_string = "".join(str(item) for item in code_items)
    password = code_string
    print(password)
    return password


def send_password(phone, password):
    import requests
    import json
    text = f'Ваш пароль от сайта kurs.stern.xyz: {password}'
    phone = ''#Delete it
    url = 'http://api.sms-prosto.ru/' \
          '?method=push_msg&key={}&text={}&phone={}&sender_name={}&priority=1&format=json' \
        .format(SMS_SENDER_API_KEY, text, phone, SMS_SENDER_NAME)
    first_response = json.loads(requests.get(url).text)

    url = 'http://api.sms-prosto.ru/' \
          '?method=push_msg&route=tg&key={}&text={}&phone={}&sender_name={}&priority=1&format=json' \
        .format(SMS_SENDER_API_KEY, text, phone, SMS_SENDER_NAME)
    second_response = json.loads(requests.get(url).text)
    if first_response['response']['msg']['err_code'] == "0":
        return True
    return False


def get_certificate(course, student):
    import requests
    import json

    first_name = student.first_name
    last_name = student.last_name
    title = course.title
    certificate = Certificate.objects.filter(course=course, user=student)
    if certificate.first():
        return False

    certificate = Certificate(course=course, user=student)
    certificate.save()
    doc_id = ""
    data = [{"%first_name": first_name, "%last_name": last_name, "%title": title}]
    data = json.dumps(data)
    url_post = 'https://gramotadel.express/api/v1/create/'
    init_payload = {
        'secure': SECURE,
        'doc_id': doc_id,
        'mask': data,
    }

    post_request = requests.post(url_post, data=init_payload)
    if post_request.json()['result'] == "error":
        return False

    time.sleep(5)
    download_file_id = post_request.json()['files'][0]
    download_url = post_request.json()['url']
    url_get = f'https://gramotadel.express/getfile/{download_file_id}/pdf/'
    file = requests.get(url_get)

    if file.status_code == 200:
        pdf_file = SimpleUploadedFile(f"{first_name}_{last_name}_{course.title}.pdf", file.content,
                                      content_type="application/vnd.pdf")
        certificate.file = pdf_file
        certificate.save()
        return download_url


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError('The given phone must be set')
        self.phone = phone
        self.password = generate_password()
        print(self.password)
        user = CustomUser(phone=phone, **extra_fields)
        user.set_password(self.password)
        user.save(using=self._db)
        return user
        #if send_password(phone, self.password):
        #    print('-------------------------------->>>>>>Successful')
        #    user.set_password(self.password)
        #    user.save(using=self._db)
        #    return user
        #return None

    def create_user(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if not phone:
            raise ValueError('The given phone must be set')
        self.phone = phone
        self.password = password
        user = CustomUser(phone=phone, **extra_fields)
        #user.set_password(self.password)
        #user.save(using=self._db)
        #return user
        if send_password(phone, self.password):
            user.set_password(self.password)
            user.save(using=self._db)
            return user
        return None

    def create_superuser(self, phone, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, **extra_fields)


class CustomUser(AbstractUser):

    username = None
    first_name = models.CharField('Имя', max_length=255, unique=False)
    last_name = models.CharField('Фамилия', max_length=255, unique=False)
    patronymic = models.CharField('Отчество', max_length=255, unique=False, null=True, blank=True)
    description = models.CharField('Описание', max_length=600, default='', null=True, blank=True)
    picture = models.ImageField('Аватарка', null=True, blank=True, storage=storage, upload_to=r'media/teacher')
    user_type = models.CharField('Преподаватель/студент', choices=USER_ROLES, max_length=255, default='student')
    phone = PhoneNumberField('Телефон', region='RU', unique=True)
    is_active = models.BooleanField('Активен', default=True)
    password = models.CharField('Проверочный код', unique=True, max_length=5)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Homework(models.Model):
    title = models.CharField('Название', max_length=255)
    teacher = models.ForeignKey(CustomUser, max_length=255, on_delete=models.CASCADE)
    file = models.FileField('Домашнее задание', storage=storage, upload_to=r'media/homework/', null=True, blank=True) #upload_to=r'homework/'
    video = models.OneToOneField('Videos', on_delete=models.CASCADE, null=True, blank=True, related_name='homework')

    class Meta:
        verbose_name = 'Домашнее задание'
        verbose_name_plural = 'Домашнее задание'

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг курса',
                            blank=True,
                            unique=True,
                            help_text='Ссылка на ЛК: site.ru/courses/[slug]. Заполняется автоматически')
    intro = models.ImageField('Обложка', null=True, blank=True, storage=storage, upload_to=r'media/course/intro/')
    description = models.CharField('Описание',
                                   max_length=600,
                                   default='')
    tg_link = models.URLField('Ссылка на ТГ канал', default='')
    cost = models.DecimalField(max_digits=8, decimal_places=0, null=True, blank=True)
    paid = models.BooleanField('Платный курс', default=True)
    teacher = models.ForeignKey(CustomUser, max_length=255, on_delete=models.PROTECT, blank=True, related_name='teacher')
    student = models.ManyToManyField(CustomUser, max_length=255, blank=True, related_name='student')
    form = models.ManyToManyField('Form', related_name='form', blank=True)
    aim = models.ManyToManyField('Aim', related_name='aim', blank=True)
    study = models.ManyToManyField('Study', related_name='study', blank=True)

    def get_absolute_url(self):
        return reverse_lazy('course', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.title = self.title.strip()
        if self.slug == '':
            self.slug = slugify('{}-{}'.format(self.title.lower(), rnd(0, 9999)))
        else:
            self.slug = self.slug.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


@receiver(m2m_changed, sender=Course.student.through)
def course_add_student(pk_set, instance, action, **kwargs):
    if action == 'post_add':
        for i in pk_set:
            student = CustomUser.objects.get(pk=i)
            get_certificate(course=instance, student=student)
        return True


class PaidForCourse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='paid_for_course')
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_status = models.BooleanField('Платеж выполнен', default=False)

    def __str__(self):
        return f'{self.user} {self.course}'

    class Meta:
        verbose_name = 'Оплата курса'
        verbose_name_plural = 'Оплата курса'


class Aim(models.Model):
    text = models.CharField('Цель', max_length=600)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'


class Form(models.Model):
    text = models.CharField('Класс', max_length=20)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'


class Study(models.Model):
    text = models.CharField('Предмет', max_length=600)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificate')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField('Сертификат', storage=storage, upload_to=r'media/certificate/', null=True, blank=True) #upload_to=r'certificate/'
    finished_course = models.BooleanField('Курс закончен', default=False)

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'

    def __str__(self):
        return f'{self.user} - {self.course}'


class Webinar(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='webinar')
    date = models.DateField('Дата вебинара', auto_now_add=False)

    class Meta:
        verbose_name = 'Вебинар'
        verbose_name_plural = 'Вебинары'

    def __str__(self):
        return str(self.date)


class StudentWebinar(models.Model):
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='student_webinar')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Вебинары студентов'
        verbose_name_plural = 'Вебинары студентов'

    def __str__(self):
        return f'{str(self.student)}: {str(self.webinar)}'


class Videos(models.Model):
    course = models.ForeignKey(Course, max_length=255, on_delete=models.CASCADE, related_name='videos')
    number = models.DecimalField('Номер лекции', max_digits=2, decimal_places=0)
    title = models.CharField('Название', max_length=255)
    video = models.FileField('Видео', storage=storage, upload_to=r'media/course/video')
    short_video = models.FileField('Короткое видео', storage=storage, upload_to=r'media/course/video', null=True, blank=True)
    intro = models.ImageField('Превью', null=True, blank=True, storage=storage, upload_to=r'media/course/video/intro')
    slug = models.SlugField('Слаг видео',
                            blank=True,
                            unique=True,
                            help_text='Ссылка на курс: site.ru/courses/[slug]. Заполняется автоматически')
    description = models.CharField('Описание видео', max_length=600, default='')
    start_time = models.DecimalField('Начальная секунда обрезания видео', max_digits=5, decimal_places=0, default=1)
    end_time = models.DecimalField('Конечная секунда обрезания видео', max_digits=5, decimal_places=0, default=180)

    def get_absolute_url(self):
        return reverse_lazy('open_video', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.title = self.title.strip()
        if self.slug == '':
            self.slug = slugify('{}-{}'.format(self.title.lower(), rnd(0, 9999)))
        else:
            self.slug = self.slug.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'


class Test(models.Model):
    video = models.OneToOneField(Videos, on_delete=models.CASCADE, null=True, blank=True, related_name='tests')
    file = models.FileField('Разбор теста', storage=storage, upload_to=r'media/test/', null=True, blank=True)#upload_to=r'test/'

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return str(self.video)


class Questions(DirtyFieldsMixin, models.Model):
    text = models.TextField('Формулировка задания', default='')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    latex_text = models.JSONField('Латех', null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new or 'text' in self.get_dirty_fields() or not self.latex_text:
            string = self.text
            pattern = r'(\$[^$]+\$)'
            parts = re.split(pattern, string)
            result = []
            current_text = ''

            for part in parts:
                if part.startswith('$') and part.endswith('$'):
                    if current_text.strip():
                        result.append(current_text.strip())
                        current_text = ''
                    result.append(part)
                else:
                    current_text += part.strip()

            if current_text:
                result.append(current_text.strip())
            self.latex_text = json.dumps(result)
            super().save(*args, **kwargs)


class Answers(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answers')
    answer = models.CharField('Ответ', max_length=255, default='')
    right = models.BooleanField('Верный', default=False)

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='user_answer')
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'


class CompletedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='completed_test')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    result = models.CharField('Результат', max_length=25, null=True, blank=True)
    completed_date = models.DateTimeField('Дата прохождения', auto_now_add=True)
    success = models.BooleanField('Пройден успешно', default=False)

    def __str__(self):
        return f'{self.user} {self.test}'

    class Meta:
        verbose_name = 'Тесты пользователей'
        verbose_name_plural = 'Тесты пользователей'


class CountCompletedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='count_unsuccess_test')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    count = models.DecimalField('Кол-во', max_digits=2, decimal_places=0)

    def __str__(self):
        return f'{self.user} {self.test}'

    class Meta:
        verbose_name = 'Кол-во неправильных тестов пользователей'
        verbose_name_plural = 'Кол-во неправильных тестов пользователей'


class UsersActiveVideo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Videos, on_delete=models.CASCADE, related_name='is_active')
    active = models.BooleanField('Активно', default=False)

    def __str__(self):
        return f'{self.user} {self.video}'

    class Meta:
        verbose_name = 'Активное видео пользователя'
        verbose_name_plural = 'Активные видео пользователя'


class Advertisement(models.Model):
    title = models.CharField('Название новости', max_length=255)
    text = RichTextUploadingField('Текст новости')
    description = models.CharField('Описание',
                                   max_length=300,
                                   default='')
    image = models.ImageField('Картинка', storage=storage, upload_to=r'media/advertisement/image/', null=True, blank=True)
    slug = models.SlugField('Слаг новости',
                            blank=True,
                            unique=True,
                            help_text='Ссылка на blog: site.ru/advertise/[slug]. Заполняется автоматически')

    def get_absolute_url(self):
        return reverse_lazy('advertise', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.title = self.title.strip()
        if self.slug == '':
            self.slug = slugify('{}-{}'.format(self.title.lower(), rnd(0, 9999)))
        else:
            self.slug = self.slug.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sender", on_delete=models.PROTECT)
    message = models.TextField("Сообщение")
    pub_date = models.DateTimeField('Дата сообщения', default=timezone.now)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.message}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AnswerMessage(models.Model):
    message = models.ForeignKey(Message, related_name="answer", on_delete=models.PROTECT)
    text = models.TextField("Сообщение")
    pub_date = models.DateTimeField('Дата сообщения', default=timezone.now)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Ответы на сообщения'
        verbose_name_plural = 'Ответы на сообщения'

    def __str__(self):
        return f'{self.message}'


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class Feedback(models.Model):
    fio = models.CharField('ФИО', max_length=255, null=True, blank=True)
    text = models.TextField("Текст отзыва", null=True, blank=True)
    link = models.URLField('Ссылка', default='', null=True, blank=True)
    phone = PhoneNumberField('Телефон', region='RU')
    is_published = models.BooleanField('Опубликовано', default=False)
    is_processed = models.BooleanField('Обработано', default=False)

    def __str__(self):
        return 'Отзывы'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class UserQuestions(models.Model):
    text_question = models.TextField("Текст вопроса")
    text_answer = models.TextField("Текст ответа", null=True, blank=True)
    name = models.CharField('Имя', max_length=255)
    phone = PhoneNumberField('Телефон', region='RU')

    def __str__(self):
        return 'Вопросы'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class SiteSettings(SingletonModel):
    title = models.CharField('Заголовок сайта', max_length=150, blank=True, default='')
    description = models.TextField('Описание сайта', help_text='Используется в meta description',
                                   blank=True,
                                   max_length=150, )
    phone = models.CharField('Телефон', max_length=150, blank=True, default='')
    email = models.EmailField('Электронная почта', blank=True, default='')
    telegram = models.URLField('Телеграм', blank=True, default='')
    instagram = models.URLField('Инстаграм', blank=True, default='')
    facebook = models.URLField('Фейсбук', blank=True, default='')
    youtube = models.URLField('Ютуб', blank=True, default='')
    whatsapp = models.URLField('Вотсап', blank=True, default='')

    def __str__(self):
        return 'Настройки сайта'

    class Meta:
        verbose_name = 'настройки сайта'
        verbose_name_plural = 'настройки сайта'

