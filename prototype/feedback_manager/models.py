from __future__ import unicode_literals

import datetime

from django.db import models
from django.contrib.auth.models import User

type_status = (('A', 'Active'), ('I', 'Inactive'))

feedback_status = (
	('I', 'In Progress'),
	('C', 'Complete'),
	('A', 'Assigned'))

question_types = (
	('S','Subjective'),
	('O','Objective'))

class Question(models.Model):
	text = models.TextField()
	status = models.CharField(max_length=10, choices=type_status, default='A')
	question_type = models.CharField(max_length=1, choices=question_types, default='S')

	def __str__(self):
		return self.text

	def is_subjective(self):
		if self.question_type == 'S':
			return True
		return False

class FeedbackType(models.Model):
	name = models.CharField(max_length=48, unique=True)
	questions = models.ManyToManyField(Question)
	status = models.CharField(max_length=10, choices=type_status, default='A')

	def __str__(self):
		return self.name

class Feedback(models.Model):
	name = models.CharField(max_length=48)
	feedback_type = models.ForeignKey(FeedbackType, null=True)
	user = models.ForeignKey(User, related_name='assigned_feedbacks')
	created_by = models.ForeignKey(User, related_name='feedbacks')
	code = models.CharField(max_length=16, unique=True, blank=True)
	started_on = models.DateTimeField(null=True)
	ended_on = models.DateTimeField(null=True)
	status = models.CharField(max_length=10, choices=feedback_status, default='A')
	questions = models.ManyToManyField(Question, through='FeedbackQusetionMap')

	def start_feedback(self):
		self.status = 'I'
		self.started_on = datetime.datetime.now()
		self.save()

	def end_feedback(self):
		self.status = 'C'
		self.ended_on = datetime.datetime.now()
		self.save()

	def is_completed(self):
		return self.status == 'C'

	def __str__(self):
		return "%s (%s)" %(self.user.get_full_name(), self.feedback_type.name)

class FeedbackQusetionMap(models.Model):
	feedback = models.ForeignKey(Feedback, null=False, related_name='map_feedbacks')
	question = models.ForeignKey(Question, null=False)
	submitted_answer = models.TextField(null=True, blank=True)
	submitted_at = models.DateTimeField(null=True, blank=True)
	
	def __str__(self):
		return str(self.feedback)

	def get_submitted_answer(self):
		"""
		"""	
		if self.question.is_subjective():
			return self.submitted_answer
		else:
			return ",".join(self.fqom.all().values_list('submitted_option__text',
				flat=True))

class Option(models.Model):
	text = models.CharField(max_length=48)
	question = models.ForeignKey(Question, null=False, related_name='options')

	def __str__(self):
		return self.text

class FeedbackQusetionOptionMap(models.Model):
	feedback_qusetion_map = models.ForeignKey(FeedbackQusetionMap, null=False, related_name="fqom")
	submitted_option = models.ForeignKey(Option, null=False, blank=True,
		related_name='submited_option')

	def __str__(self):
		return str(self.feedback_qusetion_map)

