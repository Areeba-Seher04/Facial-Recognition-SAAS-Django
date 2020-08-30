from django.db import models
from django.contrib.auth.models import AbstractUser #all functionalies are implemented like username(required),password(req) and email. we can ad more things here
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
import stripe
from django.utils import timezone
import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

MEMBERSHIP_CHOICES= (
	('F','free_trial'),
	('M','member'),
	('N','not_member'),
	)

class File(models.Model):
	file = models.ImageField()

	def __str__(self):
		return self.file.name
		
# AbstractBaseUser : Here nothing is implemented (so we dont want this)

class User(AbstractUser): #make a CUSTOM USER (so also bring it in settings.py (line 100))
	## add additional fields in here
	is_member = models.BooleanField(default=False)
	on_free_trial = models.BooleanField(default=True) #once user will signup then automatially free trial will be start
	stripe_customer_id = models.CharField(max_length=40)

class MemberShip(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE) #one user can contain only 1 membership
	type = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES)
	start_date = models.DateTimeField() #not setting auto_now True bcz not_member have no start data
	end_date = models.DateTimeField()
	stripe_subscription_id = models.CharField(max_length=40, blank=True, null=True) #blank , null: beacuse trial have no subsciption id
	stripe_subscription_item_id = models.CharField(max_length=40, blank=True, null=True) #imp for creating a usage record : views lines 209

	def __str__(self):
		return self.user.username


class Payment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	amount = models.FloatField()

	def __str__(self):
		return self.user.username


class TrackedRequest(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE) #one user can have many requests (1-many relation)
	endpoint = models.CharField(max_length= 200) #which endpoint you want to track
	timestamp = models.DateTimeField(auto_now_add=True) #used to filter how many req user made in last month or last day etc
	usage_record_id = models.CharField(max_length=50, blank=True, null=True) #null, blank bcz this is not generated for free trials user using stripe
	
	def __str__(self):
		return self.user.username


# when we 1st create account we need customer to be on free trial and we are going to create
# a stripe customer and create the membership as well by specigying a type as free trial
# use post_save signal for that
def post_save_user_receiver(sender, instance, created, *args, **kwargs): #instance = User model instance (User will send the signal)
	if created: #if user is created
		#create customer in stripe (by using stripe api call)
		customer = stripe.Customer.create(email=instance.email) 
		instance.stripe_customer_id = customer.id
		instance.save()

		#create membership now
		membership = MemberShip.objects.get_or_create(
			user = instance,
			type = 'F',
			start_date = timezone.now(),
			end_date = timezone.now() + datetime.timedelta(14)) #freetrial will end in 14 days


def user_logged_in_receiver(sender, user, request, **kwargs): #user is instance here
	'''When user logged in then check user membership status and perform action accordig to it'''
	membership = user.membership
	if user.on_free_trial:
		#membership end date has passed
		if membership.end_date < timezone.now():
			user.on_free_trial = False
			#update the membership
			membership.type = 'N'

		elif user.is_member:
			sub = stripe.Subscription.retrieve(membership.stripe_subscription_id)
			if sub.status == 'active':
				membership.end_date = datetime.datetime.fromtimestamp(
					sub.current_period_end
					)
				#already true but again set it true if in some case it becomes false
				user.is_member = True
			else:
				user.is_member = False
				#update the membership
				membership.type = 'N'
		else:
			pass

		user.save()
		membership.save()

#link this receiver to the post_save_signal
post_save.connect(post_save_user_receiver, sender=User) 
user_logged_in.connect(user_logged_in_receiver)