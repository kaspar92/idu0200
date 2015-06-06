# coding=utf-8
from django.contrib.auth.decorators import login_required
import simplejson as json
from django.http.response import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core import serializers

# Create your views here.
from dokud.models import Document, DocType, DocumentDocType, DocCatalog, DocumentDocCatalog, Employee, Person


def documents_list(request, document_type=None):
    if document_type:
        print "Buu1!"
        document_type = get_object_or_404(DocType, type_name=document_type.replace("-", " "))
        document_ids = [ddt.document_fk for ddt in DocumentDocType.objects.filter(doc_type_fk=document_type.doc_type)]
        documents = Document.objects.filter(document__in=document_ids)
    else:
        print "Buu3!"
        documents = Document.objects.all()


    data = {
        'title': document_type.type_name if document_type else "Kõik dokumendid",
        'documents': documents
    }

    return render(request, 'documents.html', data)

def catalog_list(request, catalog_name):
    catalog = get_object_or_404(DocCatalog, name=catalog_name.replace("-", " "))
    document_ids = [ddc.document_fk for ddc in DocumentDocCatalog.objects.filter(doc_catalog_fk=catalog.doc_catalog)]
    documents = Document.objects.filter(document__in=document_ids)

    data = {
        'title': catalog.name,
        'documents': documents
    }

    return render(request, 'documents.html', data)

def document(request, id):
    document = get_object_or_404(Document, document=id)

    creator =  Employee.objects.get(employee=document.created_by)
    creator_person = Person.objects.get(person=creator.person_fk)
    creator_name = creator_person.first_name + " " + creator_person.last_name
    setattr(document, 'creator', creator_name)

    if document.updated_by:
        updater =  Employee.objects.get(employee=document.updated_by)
        updater_person = Person.objects.get(person=updater.person_fk)
        updater_name = creator_person.first_name + " " + creator_person.last_name
        setattr(document, 'updater', updater_name)
    else:
        setattr(document, 'updater', "")

    if request.is_ajax():
        return ajax_document(document)

def ajax_document(document):
    data = {
        'document': document.document,
        'name': document.name,
        'description': document.description,
        'created': document.created.isoformat(),
        'creator': document.creator,
        'updated': document.updated.isoformat() if document.updated else "",
        'updater': document.updater,
    }
    return HttpResponse(json.dumps(data))
