from django.contrib import admin
from core.models import User, MemberShip, Payment, File, TrackedRequest

admin.site.register(User)
admin.site.register(MemberShip)
admin.site.register(Payment)
admin.site.register(File)
admin.site.register(TrackedRequest)