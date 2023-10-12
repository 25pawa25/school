from django.contrib import auth
from django.contrib.auth import logout
from django.db.models import Q, Prefetch
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status, generics, viewsets, views
from study.settings import TERMINAL_KEY

from .serializers import *
from .models import *
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import requests


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['form', 'aim']

    def retrieve(self, request, slug=None):
        queryset = Course.objects.all()
        slug = get_object_or_404(queryset, slug=slug)
        serializer = AccountSerializer(slug)
        return Response(serializer.data)

    #def get_permissions(self):
    #    if self.action == 'list':
    #        permission_classes = [AllowAny]
    #    else:
    #        permission_classes = [IsAuthenticated]
    #    return [permission() for permission in permission_classes]


class MyCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = MyCoursesSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        queryset = Course.objects.filter(student=self.request.user.pk).\
            prefetch_related(Prefetch('certificate',
                                      queryset=Certificate.objects.filter(user=self.request.user)))
        serializer = MyCoursesSerializer(queryset, many=True)
        return Response(serializer.data)


class AimViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Aim.objects.all()
    serializer_class = AimSerializer
    permission_classes = (AllowAny, )


class FormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = (AllowAny, )


class StudyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = (AllowAny, )


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.pk)


class GetCertificateFromIdViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = (IsAuthenticated,)


class WebinarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Webinar.objects.all()
    serializer_class = WebinarSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def get_queryset(self):
        return self.queryset.all().prefetch_related(Prefetch('student_webinar',
                                      queryset=StudentWebinar.objects.filter(student=self.request.user)))

class StudentWebinarViewSet(viewsets.ModelViewSet):
    queryset = StudentWebinar.objects.all()
    serializer_class = StudentWebinarSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['student'] = self.request.user.id
        serializer = StudentWebinarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            queryset = StudentWebinar.objects.filter(webinar=pk, student=self.request.user)
            serializer = StudentWebinarSerializer(queryset, many=True)
            return Response(serializer.data)
        except StudentWebinar.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)




class VideosViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer
    permission_classes_by_action = {'retrieve': [IsAuthenticated],
                                    'list': [IsAuthenticated]}
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def retrieve(self, request, slug=None, *args, **kwargs):
        queryset = Videos.objects.filter(Q(slug=self.kwargs['slug']) &
                                         (Q(course__student=self.request.user) | Q(course__paid=False))).\
            prefetch_related(Prefetch('tests__completed_test',
                                      queryset=CompletedTest.objects.filter(user=self.request.user).order_by('-completed_date'))).\
            prefetch_related(Prefetch('is_active',
                                      queryset=UsersActiveVideo.objects.filter(Q(user=self.request.user) | Q(user=None)))).\
            prefetch_related(Prefetch('tests__count_unsuccess_test',
                                      queryset=CountCompletedTest.objects.filter(user=self.request.user)))
        queryset = queryset.distinct()

        if queryset.first():
            slug = get_object_or_404(queryset, slug=slug)
            serializer = VideoSerializer(slug)

        else:
            query1 = Videos.objects.all()
            slug = get_object_or_404(query1, slug=slug)
            serializer = ShortVideoSerializer(slug)

        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.all(). \
            prefetch_related(Prefetch('tests__completed_test',
                                      queryset=CompletedTest.objects.filter(user=self.request.user).order_by('-completed_date'))). \
            prefetch_related(Prefetch('is_active',
                                      queryset=UsersActiveVideo.objects.filter(Q(user=self.request.user) | Q(user=None)))). \
            prefetch_related(Prefetch('tests__count_unsuccess_test',
                                      queryset=CountCompletedTest.objects.filter(user=self.request.user)))

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except:
            return [permission() for permission in self.permission_classes]


class DescriptCourseViewSet(viewsets.ModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = ShortVideoSerializer
    permission_classes = (AllowAny, )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']


class HomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def retrieve(self, request, slug=None):
        queryset = Advertisement.objects.all()
        slug = get_object_or_404(queryset, slug=slug)
        serializer = AdvertisementSerializer(slug)
        return Response(serializer.data)


class TestsViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['video']

    def get_queryset(self):
        return self.queryset.all(). \
            prefetch_related(Prefetch('questions__answers',
                                      queryset=Answers.objects.all().order_by('-id'))). \
            prefetch_related(Prefetch('count_unsuccess_test',
                                      queryset=CountCompletedTest.objects.filter(user=self.request.user).order_by('-id'))). \
            prefetch_related(Prefetch('questions__user_answer',
                                      queryset=UserAnswer.objects.filter(user=self.request.user).order_by('-id')))


class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = UserQuestions.objects.exclude(text_answer__exact='')
    permission_classes = (AllowAny, )
    serializer_class = MainQuestionsSerializer

    def create(self, request, *args, **kwargs):
        serializer = MainQuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.filter(is_published=True)
    permission_classes_by_action = {'create': [AllowAny],
                                    'list': [AllowAny]}
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = self.request.user.id
        serializer = UserAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #def perform_create(self, serializer):
    #    serializer.validated_data['user'] = self.request.user
    #    return super(UserAnswerViewSet, self).perform_create(serializer)


class TestsResultsViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = (IsAuthenticated, )#IsAuthenticated
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question__test__video']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.pk)


class CompletedTestViewSet(viewsets.ModelViewSet):
    queryset = CompletedTest.objects.all()
    serializer_class = CompletedTestSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        #data = request.data
        #data['user'] = self.request.user.pk
        request.data._mutable = True
        data = request.data
        data['user'] = self.request.user.id
        request.data._mutable = False
        serializer = CompletedTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageListSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['pub_date']

    #def get_queryset(self):
    #    return self.queryset.filter(sender=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        user_messages = Message.objects.filter(sender=user)
        user_answers = AnswerMessage.objects.filter(message__sender=user).order_by('pub_date')
        serializer1 = MessageSerializer(user_messages, many=True)
        serializer2 = AnswerMessageSerializer(user_answers, many=True)
        combined_data = serializer1.data + serializer2.data

        combined_data = sorted(combined_data, key=lambda x: x['pub_date'])

        return Response(combined_data)


    def create(self, request):
        #data = request.data
        #data['sender'] = self.request.user.pk
        request.data._mutable = True
        data = request.data
        data['sender'] = self.request.user.id
        request.data._mutable = False
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SiteSettingsAPIList(generics.ListAPIView):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer


class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = (AllowAny, )


def logout_user(request):
    logout(request)
    return redirect('home')


class RegistrationView(viewsets.ModelViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = (
        AllowAny,
    )

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_success_url(self):
        return reverse('api/v1/confirm/')


class ConfirmationView(viewsets.ModelViewSet):
    serializer_class = ConfirmationSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'phone'

    def put(self, request, phone=None):
        instance = CustomUser.objects.get(phone=phone)
        serializer = ConfirmationSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_success_url(self):
        return reverse('api/v1/account/')


class ChangePasswordView(viewsets.ModelViewSet):
    serializer_class = ChangePasswordSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'phone'

    def put(self, request, phone=None):
        instance = CustomUser.objects.get(phone=phone)
        serializer = ChangePasswordSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(f'------------->>>{serializer.data.get("password")}')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckPhoneView(viewsets.ModelViewSet):
    serializer_class = ChangePasswordSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['phone']


class InitPaidForCourseViewSet(viewsets.ModelViewSet):
    queryset = PaidForCourse.objects.all()
    serializer_class = PaidForCourseSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        try:
            instance = PaidForCourse.objects.get(course=request.data.get("course"), user=self.request.user.id)
            order_id = instance.order_id

        except:
            request.data._mutable = True
            data = request.data
            data['user'] = self.request.user.id
            request.data._mutable = False
            serializer = PaidForCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            order_id = PaidForCourse.objects.get(course=serializer.data.get('course'),
                                                 user=serializer.data.get('user')).order_id

        amount = str(Course.objects.get(id=request.data.get("course")).cost * 100)
        description = Course.objects.get(id=request.data.get("course")).title
        phone = self.request.user.phone

        init_url = 'https://securepay.tinkoff.ru/v2/Init'
        init_payload = {
            'TerminalKey': TERMINAL_KEY,
            'Amount': amount,
            'OrderId': str(order_id),
            'Description': description,
            'PayType': 'O',
            'SuccessURL': '',
            'FailURL': '',
            'NotificationURL': '',
            'Receipt': {
                'Phone': str(phone),
                'Taxation': 'usn_income',
                "Items": [
                    {
                        "Name": description,
                        "Price": amount,
                        "Quantity": 1.00,
                        "Amount": amount,
                        "Tax": "vat10",
                    },
                ]
            }
        }
        init_headers = {
            'Content-Type': 'application/json'
        }
        init_response = requests.post(init_url, headers=init_headers, json=init_payload)

        if init_response.status_code != 200:
            return Response({'error': 'Ошибка инициализации платежа'}, status=400)

        init_data = init_response.json()
        payment_url = init_data['PaymentURL']

        return Response(payment_url, status=status.HTTP_200_OK)


class PaidForCourseViewSet(viewsets.ModelViewSet):
    queryset = PaidForCourse.objects.all()
    serializer_class = PaidForCourseSerializer

    def update(self, request, *args, **kwargs):
        payment_status = request.data.get('Status')
        order_id = request.data.get('OrderId')
        instance = PaidForCourse.objects.get(order_id=order_id)
        if payment_status == 'CONFIRMED':
            instance.payment_status = True
            instance.save()
            course = instance.course
            course.student.add(instance.user)
            return HttpResponse('OK', status=200)
        else:
            return HttpResponse('NOT OK', status=400)


