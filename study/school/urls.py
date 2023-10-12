from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *

#router = routers.SimpleRouter()
#router.register(r'index', HomeViewSet)
#router.register(r'account', AccountViewSet)
#router.register(r'course', CourseViewSet)


urlpatterns = [
    path('api/v1/', HomeViewSet.as_view({'get': 'list'})),
    path('api/v1/<slug:slug>', HomeViewSet.as_view({'get': 'retrieve'})),
    path('logout/', logout_user, name='logout'),
    path('api/v1/account/', AccountViewSet.as_view({'get': 'list'})),
    path('api/v1/account/<slug:slug>', AccountViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/mycourses/', MyCoursesViewSet.as_view({'get': 'list'})),
    path('api/v1/paid/', InitPaidForCourseViewSet.as_view({'post': 'create'})),
    path('api/v1/add_student/', PaidForCourseViewSet.as_view({'post': 'create'})),
    path('api/v1/aim/', AimViewSet.as_view({'get': 'list'})),
    path('api/v1/form/', FormViewSet.as_view({'get': 'list'})),
    path('api/v1/study/', StudyViewSet.as_view({'get': 'list'})),
    path('api/v1/certificate/', CertificateViewSet.as_view({'get': 'list'})),
    path('api/v1/certificate/<int:pk>', GetCertificateFromIdViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/webinar/', WebinarViewSet.as_view({'get': 'list'})),
    path('api/v1/webinar/add_student/', StudentWebinarViewSet.as_view({'post': 'create'})),
    path('api/v1/webinar/<int:pk>/', StudentWebinarViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/videos/', VideosViewSet.as_view({'get': 'list'})),
    path('api/v1/videos/<slug:slug>', VideosViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/description/', DescriptCourseViewSet.as_view({'get': 'list'})),
    path('api/v1/tests/', TestsViewSet.as_view({'get': 'list'})),
    path('api/v1/tests/<int:pk>', CompletedTestViewSet.as_view({'post': 'create'})),
    path('api/v1/tests/question/', UserAnswerViewSet.as_view({'post': 'create'})),
    path('api/v1/tests/result', TestsResultsViewSet.as_view({'get': 'list'})),
    path('api/v1/main_questions/', QuestionsViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/v1/feedback/', FeedbackViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/v1/sitesettings/', SiteSettingsViewSet.as_view({'get': 'list'})),
    path('api/v1/message/', MessageViewSet.as_view({'get': 'list', 'post': 'create'})),
    #path('api/v1/acquiring/', PaymentView.as_view()),
    path('api/v1/register/', RegistrationView.as_view({'post': 'create'}), name='register'),
    path('api/v1/confirm/<phone>/', ConfirmationView.as_view({'put': 'update', 'get': 'retrieve'}), name='confirm'),
    path('api/v1/changepass/<phone>/', ChangePasswordView.as_view({'put': 'update'}), name='changepass'),
    path('api/v1/check_phone/', CheckPhoneView.as_view({'get': 'list'})),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    #path(r'notification/', Notification.as_view(), name='notification'),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
