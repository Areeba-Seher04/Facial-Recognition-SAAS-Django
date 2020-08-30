from django.urls import path
from .views import (
	FileUploadView,
	ChangeEmailView,
	UserEmailView,
	ChangePasswordView,
	UserDetailView,
	SubscribeView,
	ImageRecogitionView,
	APIKeyView,
	CancelSubscription
	)

app_name = 'core'

urlpatterns = [
	path('demo/', FileUploadView.as_view(), name='file-ipload-view'),
	path('change-email/', ChangeEmailView.as_view(), name='change-email'),
	path('email/', UserEmailView.as_view(), name='email'),
	path('change-password/', ChangePasswordView.as_view(), name='change-password'),
	path('billing/', UserDetailView.as_view(), name='billing'),
	path('subscribe/', SubscribeView.as_view(), name='subscribe'),
	path('cancel-subscribe/', CancelSubscription.as_view(), name='cancel-subscribe'),
	path('upload/' ,ImageRecogitionView.as_view(), name='image-recognition'),
	path('api-key/' ,APIKeyView.as_view(), name='api-key')


]