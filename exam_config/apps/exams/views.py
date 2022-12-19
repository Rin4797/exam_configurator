from django.shortcuts import render
# Create your views here.
from django.core.files.base import ContentFile
import os


from PyPDF2 import PdfMerger, PdfFileReader
from django.core.files import File

from django.http import HttpResponse, Http404, HttpResponseRedirect, FileResponse
from django.urls import reverse
from .models import Exam, Question

def index(request):
    exam_list = Exam.objects.order_by('date')
    return render(request, 'exams/exam_list.html', {'exam_list': exam_list})

def config(request):
    return HttpResponse("Add exam")

def exam_page(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q_list = Question.objects.filter(exam = exam)
        if q_list.count() != exam.num_question:
            raise Http404("Экзамен в стадии разработки, напишите @%s, это %s" % (exam.creator, q_list.count()))
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
        if q_list.count() != exam.num_question:
            raise Http404("Экзамен в стадии разработки, напишите @%s, это %s" % (exam.creator, q_list.count()))
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

def add_file(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    if request.FILES['file']:
        q.answer = request.FILES["file"]
        q.save()
    if 'status' in request.POST:
        q.finished = True
    else:
        q.finished = False
    q.save()
    return HttpResponseRedirect(reverse('exams:q_page', args=(exam.id, q.id)))

def add_question(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    exam.num_question += 1
    q = Question(exam=exam, author="MarinaR1411", text=request.POST['text'], number=exam.num_question, finished=False,
                 answer=ContentFile(b"", name="%s/%s.pdf" % (exam.name, exam.num_question)))
    q.save()
    exam.save()
    return HttpResponseRedirect(reverse('exams:exam_page', args=(exam.id, )))

def add_exam(request):
    exam = Exam(name=request.POST['name'], date=request.POST['date'], creator="MarinaR1411", num_question=0,
                result=ContentFile(b"", name="%s/result.pdf" % (request.POST['name'],)))
    exam.save()
    return HttpResponseRedirect(reverse('exams:index'))

def delete_exam(request, exam_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    #os.remove(os.path.join("data", exam.name))
    exam.delete()
    return HttpResponseRedirect(reverse('exams:index'))

def delete_question(request, exam_id, q_id):
    try:
        exam = Exam.objects.get( id = exam_id)
    except:
        raise Http404("Экзамена не существует")
    try:
        q = Question.objects.get(id=q_id)
    except:
        raise Http404("Вопроса не существует")
    q.exam.num_question -= 1
    q.delete()
    return HttpResponseRedirect(reverse('exams:exam_page', args=(exam.id, )))
