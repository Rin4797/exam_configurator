from django.shortcuts import render
# Create your views here.
from django.core.files.base import ContentFile
import os
from django.contrib.auth.decorators import login_required, permission_required


from PyPDF2 import PdfMerger, PdfFileReader
from django.core.files import File

from django.http import HttpResponse, Http404, HttpResponseRedirect, FileResponse
from django.urls import reverse
from .models import Exam, Question

def index(request):
    exam_list = Exam.objects.order_by('date')
    return render(request, 'exams/exam_list.html', {'exam_list': exam_list, 'tag': ""})

def course(request, grade):
    exam_list = Exam.objects.filter(grade=grade).order_by('date')
    return render(request, 'exams/exam_list.html', {'exam_list': exam_list, 'tag': str(grade)+"-го курса"})

def config(request):
    return HttpResponse("Add exam")

def exam_page(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q_list = Question.objects.filter(exam = exam)
    except:
        raise Http404("Экзамен в стадии разработки, напишите @%s для ускорения процесса" % exam.creator)
    return render(request, 'exams/exam_page.html', {'exam': exam, 'q_list': q_list})

def exam_result(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q_list = Question.objects.filter(exam = exam)
    except:
        raise Http404("Экзамен в стадии разработки, напишите @%s для ускорения процесса" % exam.creator)
    result = PdfMerger()
    if len(q_list) == 0:
        result.append('data/blank.pdf')
    else:
        for q in q_list:
            if q.finished:
                result.append(q.answer)
    result.write(exam.result.name)
    # exam.result = File(open('%s_result.pdf' % exam.name, 'w'))
    # os.remove(exam.result.name)
    exam.save()
    return FileResponse(exam.result, as_attachment=True)

def q_page(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id = q_id)
    except:
        raise Http404("Вопроса не существует")
    return render(request, 'exams/q_page.html', {'q': q})

@login_required
def add_file(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    q.author = request.user.username
    if request.FILES['file']:
        q.answer = request.FILES["file"]
        q.save()
    q.save()
    return HttpResponseRedirect(reverse('exams:q_page', args=(exam.id, q.id)))

@login_required
def change_text(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    if request.user.username != exam.creator:
        raise Http404("Отказано в доступе. Экзамен редактирует только владелец")
    if 'text' in request.POST:
        q.text = request.POST['text']
    q.save()
    return HttpResponseRedirect(reverse('exams:q_page', args=(exam.id, q.id)))

def finish_question(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    if not q.finished:
        exam.num_finished += 1
        q.finished = True
    exam.save()
    q.save()
    return HttpResponseRedirect(reverse('exams:q_page', args=(exam.id, q.id)))

@login_required
def add_question(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    if request.user.username != exam.creator:
        raise Http404("Отказано в доступе. Экзамен редактирует только владелец")
    exam.num_question += 1
    q = Question(exam=exam, author="MarinaR1411", text=request.POST['text'], number=exam.num_question, finished=False,
                 answer=ContentFile(b"", name="%s/%s.pdf" % (exam.name, exam.num_question)))
    q.save()
    exam.save()
    return HttpResponseRedirect(reverse('exams:exam_page', args=(exam.id, )))

@login_required
def add_exam(request):
    exam = Exam(name=request.POST['name']+'_'+request.POST['grade']+'_'+request.POST['year'], date=request.POST['date'],
                grade=request.POST['grade'], num_finished=0,
                creator=request.user.username, num_question=request.POST['num_q'],
                result=ContentFile(b"", name="%s/result.pdf" % (request.POST['name'],)))
    exam.save()
    for i in range(int(request.POST['num_q'])):
        q = Question(exam=exam, author="", text="", number=i+1, finished=False,
                     answer=ContentFile(b"", name="%s/%s.pdf" % (exam.name, exam.num_question)))
        q.save()
    return HttpResponseRedirect(reverse('exams:index'))

@login_required
def delete_exam(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    if request.user.username != exam.creator:
        raise Http404("Отказано в доступе. Экзамен редактирует только владелец")
    #os.remove(os.path.join("data", exam.name))
    exam.delete()
    return HttpResponseRedirect(reverse('exams:index'))

@login_required
def delete_question(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    if request.user.username != exam.creator:
        raise Http404("Отказано в доступе. Экзамен редактирует только владелец")
    q.delete()
    return HttpResponseRedirect(reverse('exams:exam_page', args=(exam.id, )))
