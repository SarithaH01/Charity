from django.contrib import admin
from .models import userProfile,Event,Donation,Account,Blog,Track
# Register your models here.
admin.site.register(userProfile)
admin.site.register(Event)
admin.site.register(Donation)

admin.site.register(Blog)


