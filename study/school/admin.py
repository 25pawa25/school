from django.contrib import admin
from django.utils.safestring import mark_safe
from nested_admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline
from django import forms
from .models import *
from .tasks import save_short_video, active_video


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug')
    fieldsets = (
        ('Новости', {
            'fields': ('title',
                       'description',
                       'text',
                       'image',
                       'slug',
                       ),
        }),
    )

    prepopulated_fields = {"slug": ("title",)}

    def display_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f'<a href="{url}">{url}</a>')

    display_link.short_description = 'Ссылка'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'first_name', 'last_name', 'user_type', 'password', )
    fieldsets = (
        ('Пользователь', {
            'fields': ('first_name',
                       'last_name',
                       'patronymic',
                       'description',
                       'phone',
                       'user_type',
                       'picture',
                       ),
        }),

    )

    def save_model(self, request, obj, form, change):
        obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Aim)
class AimAdmin(admin.ModelAdmin):
    list_display = ('text', )
    fieldsets = (
        ('Цель', {
            'fields': ('text', ),
        }),
    )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('text', )
    fieldsets = (
        ('Класс', {
            'fields': ('text', ),
        }),
    )


@admin.register(UserQuestions)
class MainQuestionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'text_question', 'text_answer',)
    fieldsets = (
        ('Вопросы', {
            'fields': ('name', 'phone', 'text_question', 'text_answer',),
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_processed', 'is_published', 'fio', 'link')
    fieldsets = (
        ('Вопросы', {
            'fields': ('fio', 'text', 'link', 'phone', 'is_published', 'is_processed'),
        }),
    )


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ('text', )
    fieldsets = (
        ('Предмет', {
            'fields': ('text', ),
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'finished_course',)
    fieldsets = (
        ('Сертификат', {
            'fields': ('course', 'user', 'file', 'finished_course'),
        }),
    )


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', )
    list_filter = ('course', 'date', )
    fieldsets = (
        ('Вебинары', {
            'fields': ('course', 'date', ),
        }),
    )


@admin.register(StudentWebinar)
class StudentWebinarAdmin(admin.ModelAdmin):
    list_display = ('student', 'webinar', )
    list_filter = ('student', 'webinar',)
    fieldsets = (
        ('Вебинары студентов', {
            'fields': ('student', 'webinar', ),
        }),
    )


class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(user_type='teacher')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'cost', 'paid',)
    fieldsets = (
        ('Курс', {
            'fields': ('title',
                       'description',
                       'intro',
                       'cost',
                       'paid',
                       'slug',
                       'teacher',
                       'student',
                       'form',
                       'aim',
                       'study',
                       ),
        }),

    )
    prepopulated_fields = {"slug": ("title",)}
    form = CourseAdminForm

    def display_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f'<a href="{url}">{url}</a>')

    display_link.short_description = 'Ссылка'


@admin.register(PaidForCourse)
class PaidForCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', )
    list_filter = ('user', 'course',)
    fieldsets = (
        ('Оплата', {
            'fields': ('user', 'course', 'order_id', 'payment_status'),
        }
         ),
    )
    readonly_fields = (
        'order_id',
    )


class AnswersInline(NestedTabularInline):
    model = Answers
    extra = 0
    fieldsets = (
        ('Ответы', {
            'fields': ('question', 'answer', 'right',),
        }
         ),
    )


class QuestionsInline(NestedTabularInline):
    model = Questions
    inlines = (AnswersInline, )
    extra = 0
    fieldsets = (
        ('Вопросы', {
            'fields': ('test', 'text', ),
        }
         ),
    )


class TestInline(NestedTabularInline):
    model = Test
    inlines = (QuestionsInline,)
    extra = 1


class HomeworkInline(NestedTabularInline):
    model = Homework
    extra = 1
    fieldsets = (
        ('Домашнее задание', {
            'fields': ('title', 'file', 'teacher', ),
        }
         ),
    )


#@admin.register(Homework)
#class HomeworkAdmin(admin.ModelAdmin):
#    list_display = ('title', 'teacher', 'text')
#    fieldsets = (
#        ('Домашнее задание', {
#            'fields': ('title', 'text', 'teacher', 'video', ),
#        }),
#    )


@admin.register(Videos)
class VideosAdmin(NestedModelAdmin):
    inlines = (HomeworkInline, TestInline,)
    list_display = ('title', 'course', 'short_video')
    fieldsets = (
        ('Содержимое видео', {
            'fields': ('course', 'number', 'title', 'description', 'video', 'short_video', 'intro',
                       ('start_time', 'end_time'), 'slug', ),
        }),

    )

    prepopulated_fields = {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_short_video(obj.id, obj.start_time, obj.end_time)
        active_video(obj.id)


@admin.register(CompletedTest)
class CompletedTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'result', 'success', 'completed_date',)
    list_filter = ('user', 'test',)
    fieldsets = (
        ('Завершен', {
            'fields': ('user', 'test', 'result', 'success', 'completed_date',),
        }
         ),
    )
    readonly_fields = (
        'completed_date',
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(CountCompletedTest)
class CountCompletedTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'count',)
    list_filter = ('user', 'test',)
    fieldsets = (
        ('Количество', {
            'fields': ('user', 'test', 'count',),
        }
         ),
    )



@admin.register(UsersActiveVideo)
class UsersActiveVideo(admin.ModelAdmin):
    list_display = ('user', 'video', 'active',)
    list_filter = ('user', 'video', 'active',)
    fieldsets = (
        ('Активное видео', {
            'fields': ('user', 'video', 'active',),
        }),
    )


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer',)
    list_filter = ('user', 'question', 'answer',)
    fieldsets = (
        ('Цель', {
            'fields': ('user', 'question', 'answer',),
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # Создадим объект по умолчанию при первом страницы SiteSettingsAdmin со списком настроек
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # обязательно оберните загрузку и сохранение SiteSettings в try catch,
        # чтобы можно было выполнить создание миграций базы данных
        try:
            SiteSettings.load().save()
        except Exception:
            pass

    # запрещаем добавление новых настроек
    def has_add_permission(self, request, obj=None):
        return False

    # а также удаление существующих
    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description',)
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email'),
        }),
        ('Социальные сети', {
            'fields': (
                ('telegram', 'instagram', 'facebook', 'youtube', 'whatsapp', ),
            )
        })
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'message', 'pub_date', )
    date_hierarchy = 'pub_date'
    fieldsets = (
        ('Содержимое сообщения', {
            'fields': (
                'sender',
                'message',
                'pub_date',

            ),
        }),
    )

    readonly_fields = (
        'pub_date',
    )

    def has_add_permission(self, request, obj=None):
        return True


@admin.register(AnswerMessage)
class AnswerMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'pub_date', 'text',)
    date_hierarchy = 'pub_date'
    fieldsets = (
        ('Содержимое сообщения', {
            'fields': (
                'message',
                'text',
                'pub_date',

            ),
        }),
    )

    readonly_fields = (
        'pub_date',
    )

    def has_add_permission(self, request, obj=None):
        return True


admin.site.enable_nav_sidebar = False

