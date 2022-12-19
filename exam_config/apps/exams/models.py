from django.db import models
import os

# Create your models here.

class Exam(models.Model):
    name = models.CharField('название экзамена', max_length = 300)
    date = models.DateField('дата экзамена')
    creator = models.CharField('создатель', max_length = 300)
    num_question = models.IntegerField('кол-во вопросов')
    result = models.FileField('результат',  upload_to="data/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete = models.CASCADE)
    author = models.CharField('автор вопроса', max_length = 300)
    text = models.TextField('текст вопроса')
    number = models.IntegerField('номер вопроса')
    answer = models.FileField('ответ на вопрос', upload_to="data/")
    finished = models.BooleanField('статус')


    def __str__(self):
        return self.exam.name + ".%s" % self.number

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
