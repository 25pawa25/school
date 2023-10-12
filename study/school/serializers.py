from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = CustomUser
        fields = ('phone',)

    def validate_phone(self, value):
        try:
            user = CustomUser.objects.get(phone=value)
            self.user = user
            if user:
                self.fail('already_registered')
        except CustomUser.DoesNotExist:
            self.user = None
        return value

    def create(self, validated_data):
        print(validated_data)
        try:
            with transaction.atomic():
                password = generate_password()
                user = UserManager().create_user(phone=validated_data.get('phone'), password=password)
        except IntegrityError:
            self.fail('cannot_create_user')
        return user


class ConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')

    def update(self, instance, validated_data):
        try:
            instance.first_name = validated_data.get('first_name')
            instance.last_name = validated_data.get('last_name')
            instance.save()

        except IntegrityError:
            self.fail('cannot_create_user')
        return instance


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('phone', )

    def update(self, instance, validated_data):
        try:
            password = generate_password()
            send_password(validated_data.get('phone'), password)
            instance.set_password(password)
            instance.save()

        except IntegrityError:
            self.fail('cannot_change_password')
        return instance


class AnswerMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerMessage
        fields = '__all__'


class MessageListSerializer(serializers.ModelSerializer):
    #answer = AnswerMessageSerializer(many=True)

    class Meta:
        model = Message
        fields = ('sender', 'message', 'pub_date')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('sender', 'message', 'pub_date')

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        return message


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'patronymic', 'description', 'picture')


class AimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aim
        fields = '__all__'


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = '__all__'


class StudentWebinarSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentWebinar
        fields = '__all__'


class WebinarSerializer(serializers.ModelSerializer):
    student_webinar = StudentWebinarSerializer(many=True)

    class Meta:
        model = Webinar
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    aim = AimSerializer(many=True)
    form = FormSerializer(many=True)
    study = StudySerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'intro', 'description', 'tg_link', 'cost', 'student', 'teacher', 'form',
                  'aim', 'study')


class MyCoursesSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'intro', 'description', 'tg_link', 'cost', 'student', 'teacher', 'form', 'aim',
                  'certificate')


class PaidForCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaidForCourse
        fields = ('user', 'course')


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = '__all__'


class TestResultSerializer(serializers.ModelSerializer):
    answer = AnswersSerializer()

    class Meta:
        model = UserAnswer
        fields = '__all__'


class QuestionsSerializer(serializers.ModelSerializer):
    answers = AnswersSerializer(many=True)
    user_answer = TestResultSerializer(many=True)
    latex_text = serializers.SerializerMethodField()

    def get_latex_text(self, instance):
        latex_text = instance.latex_text
        if latex_text:
            return json.loads(latex_text)
        return []

    class Meta:
        model = Questions
        fields = '__all__'


class CompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompletedTest
        fields = '__all__'


class VideoForTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Videos
        fields = ('slug', )


class CountCompletedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountCompletedTest
        fields = ('count',)


class CompletedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTest
        fields = ('result', 'user', 'test', 'success')

    def create(self, validated_data):
        completed_test = CompletedTest.objects.create(**validated_data)

        prev_video_object = Videos.objects.get(tests__completed_test=completed_test.id)
        test = CompletedTest.objects.get(id=completed_test.id)
        course = prev_video_object.course
        number = prev_video_object.number + 1
        video_object = Videos.objects.filter(course=course, number=number)
        print(f'------------{test}')
        print(f'------------{test.success}')
        if video_object and test.success:
            UsersActiveVideo.objects.create(video=video_object[0], user=test.user, active=True)
        if not video_object and test.success:
            cert = Certificate.objects.get(user=test.user, course=prev_video_object.course)
            cert.finished_course = True
            cert.save()
        if test.success is not True:
            tesst = validated_data.get('test')
            all_answers = UserAnswer.objects.filter(question__in=tesst.questions.all(), user=test.user)
            all_answers.delete()
            try:
                count_tests = CountCompletedTest.objects.get(user=test.user, test=test.test)
                if count_tests:
                    count_tests.count += 1
                    count_tests.save()
            except:
                create_count_test = CountCompletedTest.objects.create(user=test.user, test=test.test, count=1)

        return completed_test


class UserAnswerSerializer(serializers.ModelSerializer):
    #user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserAnswer
        fields = ('user', 'question', 'answer')

    def create(self, validated_data):
        instance = UserAnswer.objects.filter(question=validated_data.get('question'), user=validated_data.get('user'))
        user_answer = instance.first()
        if user_answer:
            if validated_data.get('answer').question == validated_data.get('question'):
                user_answer.answer = validated_data.get('answer')
                user_answer.save()
                return user_answer
        else:
            if validated_data.get('answer').question == validated_data.get('question'):
                test = UserAnswer.objects.create(**validated_data)
                return test
        raise ValidationError('error')


class MainQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestions
        fields = '__all__'

    def create(self, validated_data):
        question = UserQuestions.objects.create(**validated_data)
        return question


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('fio', 'text', 'link', 'phone')

    def create(self, validated_data):
        question = Feedback.objects.create(**validated_data)
        return question


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__'


class VideoActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersActiveVideo
        fields = '__all__'


class ShortVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = ('id', 'number', 'course', 'title', 'short_video', 'intro', 'slug', 'description', 'intro')


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionsSerializer(many=True)
    completed_test = CompletedSerializer(many=True)
    video = VideoForTestSerializer()
    count_unsuccess_test = CountCompletedTestSerializer(many=True)

    class Meta:
        model = Test
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    homework = HomeworkSerializer()
    tests = TestSerializer()
    is_active = VideoActiveSerializer(many=True)

    class Meta:
        model = Videos
        fields = ('id', 'course', 'number', 'title', 'video', 'intro', 'slug', 'description', 'homework',
                  'tests', 'is_active')

