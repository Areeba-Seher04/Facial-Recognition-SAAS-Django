import datetime
import math
import stripe
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from core.permissions import IsMember
from core.serializers import (
	ChangeEmailSerializer,
	 ChangePasswordSerializer,
	 FileSerializer,
	 TokenSerializer,
	 SubscribeSerializer
	 )
from core.models import MemberShip, TrackedRequest, Payment
from core.image_detection import detect_faces

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY



def get_user_from_token(request):
	token = request.user.auth_token #auth key(token) of current user 91391f4c12b94b753d08008150d2315d9d8d7e1e
	print("token.user_id",token.user_id) #gives id of user (pk)  2
	user = User.objects.get(id=token.user_id) #gives user name
	return user

class FileUploadView(APIView):
	''' For DEMO File Upload | No need to make account | 3 requests/day'''
	permission_classes = (AllowAny,)
	throttle_scope = 'demo'

	def post(self, request, *args, **kwargs):
		file_serializer = FileSerializer(data = request.data)
		if file_serializer.is_valid():

			# limit the image length to 5MB
			content_length = request.META.get('CONTENT_LENGTH') #content lenght is already there in request.META but is in bytes
			if len(content_length) > 5000000:
				return Response({'message': 'Image size is greater than 5MB'}, status = HTTP_400_BAD_REQUEST)

			file_serializer.save() #it will save the image in data_base and media_dir
			#get the path of the image saved in database
			image_path = file_serializer.data.get('file') #/media/B612_20200527_195310_037.jpg
			print("image_path",image_path)
			recognition = detect_faces(image_path)
		return Response(recognition, status=HTTP_200_OK)

class UserEmailView(APIView):
	'''Gives curent user email'''
	permission_classes = (IsAuthenticated, )

	def get(self, request, *args, **kwargs):
		user = get_user_from_token(request)
		obj = {'email', user.email}
		return Response(obj, status = HTTP_200_OK)


class ChangeEmailView(APIView):
	'''Post request to change the email'''
	permission_classes = (IsAuthenticated, )

	def post(self, request, *args, **kwargs):
		#get user from token
		user = get_user_from_token(request)
		email_serializer = ChangeEmailSerializer(data=request.data)
		if email_serializer.is_valid():
			print(email_serializer.data) #it will give email and confirm_email
			email = email_serializer.data.get('email')
			confirm_email = email_serializer.data.get('confirm_email')
			if email == confirm_email:
				user.email = email
				user.save()
				return Response({'email':email}, status=HTTP_200_OK)
			return Response({'message':'The email does not match'}, status=HTTP_400_BAD_REQUEST)
		return Response({'message':'Did not receive the correct data'}, status=HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
	'''Post request to change the password'''
	permission_classes = (IsAuthenticated, )

	def post(self, request, *args, **kwargs):
		#get user from token
		user = get_user_from_token(request)
		password_serializer = ChangePasswordSerializer(data=request.data)
		if password_serializer.is_valid():
			print(password_serializer.data) #it will give email and confirm_email
			password = password_serializer.data.get('password')
			confirm_password = password_serializer.data.get('confirm_password')
			current_password = password_serializer.data.get('current_password')
			#authenticate the user by current password
			auth_user = authenticate( #authenticate() if the given credential are valid then return a user obj
				username = user.username,
				password = current_password
			)
			if auth_user is not None:
				if password == confirm_password:
					#set password
					auth_user.set_password(password)
					auth_user.save()
					return Response({"message":"password changed succesfully"},status=HTTP_200_OK)
			else:
				return Response({'message':'The password did not match'}, status=HTTP_400_BAD_REQUEST)
			return Response({'message':'Incorrect user details'}, status=HTTP_400_BAD_REQUEST)
		return Response({'message':'Did not receive the correct data'}, status=HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
	'''User details for billing'''
	permission_classes = (IsAuthenticated, )

	def get(self, request, *args, **kwargs):
		#get user form token
		user = get_user_from_token(request)
		#get user current member ship using one to one field
		membership = user.membership
		today = datetime.datetime.now()
		month_start = datetime.date(today.year, today.month, 1) # 1st date of current month and current year

		#count of total requests user make within a current month
		tracked_request_count = TrackedRequest.objects \
		.filter(user = user, timestamp__gte = month_start).count()


		amount_due = 0 #if user is not a member
		#filter the upcoming date for payment/invoices
		if user.is_member:
			amount_due = stripe.Invoice.upcoming(
				customer = user.stripe_customer_id
				)['amount_due'] / 100 #/100 for convert it from cents to dollars
			print("amount_due",amount_due)


		obj = {
			'membershipType': membership.get_type_display(),
			'free_trial_end_date' : membership.end_date, #for people on free trial
			'next_billing_date' : membership.end_date, #for members
			'api_request_count' : tracked_request_count,
			'amount_due' : amount_due
		}
		return Response(obj)


class SubscribeView(APIView):
	'''Subscribe from Free trial to membership. Amount of api call will deduct automatically 
		from account at the end of the subscription month'''
	permission_classes = (IsAuthenticated, )

	def post(self, request, *args, **kwargs):
		#get user form token
		user = get_user_from_token(request)

		#get the user membership
		membership = user.membership

		try:
			#get the stripe customer from stripe_customer_id(created when a user create an account)
			customer = stripe.Customer.retrieve(user.stripe_customer_id)
			#create test token using strip o backend
			# https://stripe.com/docs/api/tokens/create_card?lang=python

			serializer = SubscribeSerializer(data = request.data) #it will receive stripeToken (Token generated on frontend by stripe form)
			print("request.data",request.data) #stripe token.id will be passed in serializer (it will done by REACT stripe documentation)

			#serialize post data (stripeToken)
			if serializer.is_valid():
				#get stripeToken from serializer data
				stripe_token = serializer.data.get('stripeToken')
				# stripe_token = serializer.data.get('stripeToken')
				print("stripe_token",stripe_token)

				#create the stripe subscription
				subscription = stripe.Subscription.create(
					customer = customer.id,
					items = [{"plan": settings.STRIPE_PLAN_ID }]
					)
				#update the membership
				membership.stripe_subscription_id = subscription.id
				membership.stripe_subscription_item_id = subscription['items']['data'][0]['id']
				membership.type = 'M'
				membership.start_date = datetime.datetime.now()
				membership.end_date = datetime.datetime.fromtimestamp(
					subscription.current_period_end #subscription.current_period_end from STRIPE
					)
				membership.save()

				#update the user
				user.is_member = True
				user.on_free_trial = False
				user.save()

				#create the payment
				payment = Payment()
				# / 100 for converting Cents into dollars
				payment.amount = subscription.plan.amount / 100 #from stripe
				payment.user = user
				payment.save()

				return Response({'message': 'sucess'})

			else:
				return Response({'message': 'Incorrect data was received'}, status=HTTP_200_OK)

		except stripe.error.CardError as e:
			return Response({'message' : 'Your card has been declined'}, status=HTTP_400_BAD_REQUEST)
		except stripe.error.StripeError as e:
			print(e)
			return Response({'message' : 'There was an error. You have not been billed. If this persists please contact us.'}, status=HTTP_400_BAD_REQUEST)
		except Exception as e:
			print(e)
			return Response({'message' : 'We apologize for the error. We have been informed and are working on th problem'}, status=HTTP_400_BAD_REQUEST)

class CancelSubscription(APIView):
	'''Cancel the subscription and change membership status to Not member'''
	permission_classes = (IsMember, )

	def post(self, request, *args, **kwargs):
		#get user form token
		user = get_user_from_token(request)
		membership = user.membership

		#if user is on free trial so give message to go PRO
		if membership.type == 'F':
			return Response({'message' : 'Only members can cancel the subscription'})

		#update the stripe subscription (means cancel the subscription from stripe)
		try:
			sub = stripe.Subscription.retrieve(membership.stripe_subscription_id)
			sub.delete()
		except Exception as e:
			print(e)
			return Response({'message' : 'We apologize for the error. We have been informed and are working on th problem'}, status=HTTP_400_BAD_REQUEST)


		#update the user
		user.is_member = False
		user.save()

		#update the membership
		membership.type = 'N'
		membership.save()

		return Response({'message' : 'Your subscription has been cancelled'}, status=HTTP_200_OK)





class ImageRecogitionView(APIView):
	'''User on membership/ free trial(only for 14 days) can access this view (But both should
	   be login) User will be charged for api calls 0.05 for 2 api call '''
	permission_classes = (IsMember,)
	throttle_scope = 'login_upload'

	def post(self, request, *args, **kwargs):
		#get user form token
		user = get_user_from_token(request)
		membership = user.membership

		file_serializer = FileSerializer(data = request.data)
		if file_serializer.is_valid():
			usage_record_id = None #for free trials

			if user.is_member and not user.on_free_trial:
				#keep track of request user makes using stripe https://stripe.com/docs/api/usage_records/create?lang=python
				#we need to record usage only for MEMBERS 
				usage_record = stripe.UsageRecord.create(
					  quantity=1,
					  timestamp=math.floor(datetime.datetime.now().timestamp()), #math.floor beacuse stripe dont support dates in float
					  subscription_item = membership.stripe_subscription_item_id
					)
				usage_record_id = usage_record.id

			#keep track of a request user makes (in our backend)
			#when user use this class then user name , endpoint, and current time_date will save in TrackedRequest
			tracked_request = TrackedRequest()
			tracked_request.user = user
			tracked_request.usage_record_id = usage_record_id
			tracked_request.endpoint = '/api/image-recognition/'
			tracked_request.save()

			# limit the image length to 5MB
			content_length = request.META.get('CONTENT_LENGTH') #content lenght is already there in request.META but is in bytes
			if len(content_length) > 5000000:
				return Response({'message':'Image size is greater than 5MB'}, status = HTTP_400_BAD_REQUEST)

			file_serializer.save() #it will save the image in data_base and media_dir
			#get the path of the image saved in database
			image_path = file_serializer.data.get('file') #/media/B612_20200527_195310_037.jpg
			print("image_path",image_path)
			recognition = detect_faces(image_path)
			return Response(recognition, status=HTTP_200_OK)
		else:
			return Response({'message':'Received Incorrect data'}, status=HTTP_400_BAD_REQUEST)

class APIKeyView(APIView):
	'''Get user api key'''
	permission_classes = (IsAuthenticated, )

	def get(self, request, *args, **kwargs):
		#get user form token
		user = get_user_from_token(request)
		# token = request.user.auth_token
		token_qs = Token.objects.filter(user = user)
		if token_qs.exists:
			token_serializer = TokenSerializer(token_qs, many=True) #when we use many = True then we can't use data=token_qs
			try:
				return Response(token_serializer.data, status=HTTP_200_OK)
			except:
				return Response({"message": "Did not received correct data"}, status=HTTP_400_BAD_REQUEST)
		return Response({"message": "User does not exists"})

