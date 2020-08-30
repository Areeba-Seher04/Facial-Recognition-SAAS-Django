from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsMember(permissions.BasePermission):  #BasePermission :A base class from which all permissions should inherit
	''' Permit the user if user is autheticated and (a member or on a free trial)'''
	def has_permission(self, request, view):
		#check user is login or not
		if request.user.is_authenticated:
			#if user is member and on free trial then permit him
			if request.user.is_member or request.user.on_free_trial:
				return True
			else:
				raise PermissionDenied('You must be a member to make this request')
		else:
			raise PermissionDenied('You must be logged in to make this request') 
