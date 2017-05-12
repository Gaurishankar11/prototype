import random, string, datetime

from django.contrib import admin
from django.template import Context
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.admin import AdminSite
from django.core.mail import send_mail
from django.template.loader import render_to_string
from feedback_manager.models import Question, FeedbackType, Feedback,\
									FeedbackQusetionMap, Option, FeedbackQusetionOptionMap

def get_random_string(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def assign_feedback(modeladmin, request, queryset):
	feedback_types = FeedbackType.objects.all()
	for obj in queryset:
		for feedback_type in feedback_types:
			feedback_obj = Feedback(name=get_random_string(10),
									feedback_type=feedback_type,
									user=obj,
									created_by=request.user,
									code=get_random_string(16))
			feedback_obj.save()

			for question in feedback_type.questions.all():
				feedback_qusetion_map_obj = FeedbackQusetionMap(feedback=feedback_obj,
																question=question)
				feedback_qusetion_map_obj.save()
	send_mails(queryset)

assign_feedback.short_description = "Send feedback mail to selected users"

def send_mails(queryset):
	for user_obj in queryset:
		feedbacks = Feedback.objects.filter(user=user_obj, status='A')
		msg_html = render_to_string('email_temp.html', {'feedbacks': feedbacks})

		subject='Feedback Mail'
		text_content = 'imp_mail'
		send_mail(subject, text_content, 'gaurishankar.neo@gmail.com',
				  [user_obj.email], html_message=msg_html)

class user_asign_feedback(admin.ModelAdmin):
    list_display = ['username']
    ordering = ['username']
    actions = [assign_feedback]


class OptionInline(admin.TabularInline):
    model = Option

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        OptionInline,
    ]

class FeedbackAdmin(admin.ModelAdmin):
	model=Feedback
	list_display = ('user', 'feedback_type', 'status', 'view')
	list_display_links = None
	actions = None
	def view(self, obj):
		return '<a href="%s">View</a>' % (reverse('view_feedback', kwargs={'feedback_id': obj.id}))

	view.allow_tags = True
	view.short_description = 'View Feedback'


class MyAdminSite(AdminSite):
    index_title = 'Monty Python administration'


admin_site = MyAdminSite(name='myadmin')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Feedback, FeedbackAdmin)

admin.site.register(FeedbackType)
admin.site.unregister(User)
admin.site.register(User, user_asign_feedback)
