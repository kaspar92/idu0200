# coding=utf-8
import django
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from dokud.forms import DocumentForm, TeabenoueForm, ToolepingForm, YyrilepingForm, TarnelepingForm
import simplejson as json
from django.http.response import JsonResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django import forms
from django.core.signals import request_finished
from dokud.login_logic import *
from django.contrib.auth.hashers import *
import datetime


# Create your views here.
from dokud.models import *

def login_view(request):
    data = {}
    if request.method == "POST":
        username = request.POST["username"]
        try:
            user = UserAccount.objects.get(username=username, subject_type_fk=3)
            if check_password(request.POST["password"], user.passw):
                request.session['user_logged_in'] = True

                emp = Employee.objects.get(employee=user.subject_fk)
                person = Person.objects.get(person=emp.person_fk)

                request.session['user'] = {
                    'emp': int(emp.employee),
                    'first_name': person.first_name,
                    'last_name': person.last_name
                }

                return redirect('dokud.views.documents_list')
            else:
                data['error'] = "Sellist kasutaja ja parooli kombinatsiooni ei leitud!"
        except:
            data['error'] = "Sellist kasutaja ja parooli kombinatsiooni ei leitud!"

    return render(request, "login.html", data)

@must_be_logged_in
def logout(request):
    del request.session['user_logged_in']
    return redirect('dokud.views.login_view')

@must_be_logged_in
def search(request):
    if request.method == "POST":
        documents = Document.objects.filter()
        print request.POST
        if request.POST.get('document'):
            documents = documents.filter(document=request.POST.get('document'))
        if request.POST.get('name'):
            documents = documents.filter(name__icontains=request.POST.get('name'))
        if request.POST.get('description'):
            documents = documents.filter(description__icontains=request.POST.get('description'))
        if request.POST.get('status'):
            documents = documents.filter(doc_status_type_fk=request.POST.get('status'))

        if request.POST.get('catalog'):
            document_ids = [ddc.document_fk for ddc in DocumentDocCatalog.objects.filter(doc_catalog_fk=request.POST.get('catalog'))]
            documents = documents.filter(document__in=document_ids)

        if request.POST.get('updater'):
            person_ids = [p.person for p in Person.objects.filter(last_name__icontains=request.POST.get('updater'))]
            documents = documents.filter(updated_by__in=person_ids)

        if request.POST.get('creator'):
            person_ids = [p.person for p in Person.objects.filter(last_name__icontains=request.POST.get('creator'))]
            documents = documents.filter(created_by__in=person_ids)

        data = {
            'title': "Otsingutulemused",
            'active': 'otsing',
            'documents': documents.order_by('document'),
            'search': True
        }

        return render(request, 'documents.html', data)

    statuses = DocStatusType.objects.all()
    statuses_list = []
    for selection in statuses:
        statuses_list.append({'key': selection.doc_status_type, 'value': selection.type_name})

    categories = DocCatalog.objects.all()
    categories_list = []
    for category in categories:
        categories_list.append({'key': category.doc_catalog, 'value': category.name})

    data = {
        'statuses_list': statuses_list,
        'catalogs_list': categories_list,
        'csrf_token': django.middleware.csrf.get_token(request)
    }
    return render(request, "search.html", data)


@must_be_logged_in
def documents_list(request, document_type=None):
    print request.session.get('user')['emp']
    if document_type:
        document_type = get_object_or_404(DocType, type_name=document_type.replace("-", " "))
        document_ids = [ddt.document_fk for ddt in DocumentDocType.objects.filter(doc_type_fk=document_type.doc_type)]
        documents = Document.objects.filter(document__in=document_ids).order_by('document')
    else:
        documents = Document.objects.all().order_by('document')


    data = {
        'title': document_type.type_name if document_type else "Kõik dokumendid",
        'documents': documents
    }

    return render(request, 'documents.html', data)

@must_be_logged_in
def new_document(request):
    data = {
       'active': "uus_dokument"
    }

    return render(request, 'new_document.html', data)

@must_be_logged_in
def catalog_list(request, catalog_name):
    catalog = get_object_or_404(DocCatalog, name=catalog_name.replace("-", " "))
    document_ids = [ddc.document_fk for ddc in DocumentDocCatalog.objects.filter(doc_catalog_fk=catalog.doc_catalog)]
    documents = Document.objects.filter(document__in=document_ids).order_by('document')

    data = {
        'title': catalog.name,
        'documents': documents
    }

    return render(request, 'documents.html', data)

@must_be_logged_in
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

    statuses = DocStatusType.objects.all()
    statuses_list = []
    for selection in statuses:
        statuses_list.append({'key': selection.doc_status_type, 'value': selection.type_name})

    document_attributes = DocAttribute.objects.filter(document_fk=document.document)
    document_attribute_type_fks = [da.doc_attribute_type_fk for da in document_attributes]

    document_doc_type = DocumentDocType.objects.get(document_fk=document.document)
    doc_type = DocType.objects.get(doc_type=document_doc_type.doc_type_fk)

    doc_type_attributes = DocTypeAttribute.objects.filter(doc_type_fk=doc_type.doc_type).order_by('orderby')
    doc_attribute_types = DocAttributeType.objects.filter(doc_attribute_type__in=[dta.doc_attribute_type_fk for dta in doc_type_attributes])

    document_doc_catalog = DocumentDocCatalog.objects.get(document_fk=document.document)
    catalog = DocCatalog.objects.get(doc_catalog=document_doc_catalog.doc_catalog_fk)

    attributes_list = []
    for dat in doc_attribute_types:
        if dat.data_type_fk == 4:
            selection_values = AtrTypeSelectionValue.objects.filter(doc_attribute_type_fk=dat.doc_attribute_type).order_by('orderby')
            selection_list = []
            for selection in selection_values:
                selection_list.append({'key': selection.atr_type_selection_value, 'value': selection.value_text})

        if dat.doc_attribute_type in document_attribute_type_fks:
            if dat.data_type_fk == 1:
                attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name,
                                        'slug': dat.type_name.replace(" ", "_"), 'value': [da.value_text for da in document_attributes if da.document_fk==document.document and da.doc_attribute_type_fk==dat.doc_attribute_type][0]})
            if dat.data_type_fk == 2:
                attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name,
                                        'slug': dat.type_name.replace(" ", "_"), 'value': [da.value_number for da in document_attributes if da.document_fk==document.document and da.doc_attribute_type_fk==dat.doc_attribute_type][0]})
            if dat.data_type_fk == 3:
                date = [da.value_date for da in document_attributes if da.document_fk==document.document and da.doc_attribute_type_fk==dat.doc_attribute_type][0]
                attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name,
                                        'slug': dat.type_name.replace(" ", "_"), 'value': datetime.datetime.strftime(date, "%d.%m.%Y") if date else None})
            if dat.data_type_fk == 4:
                attributes_list.append({
                    'id': dat.doc_attribute_type,
                    'type': dat.data_type_fk,
                    'name': dat.type_name,
                    'slug': dat.type_name.replace(" ", "_"),
                    'selection_list': selection_list,
                    'value': [da.atr_type_selection_value_fk for da in document_attributes if da.document_fk==document.document and da.doc_attribute_type_fk==dat.doc_attribute_type][0]
                })
        else:
            if dat.data_type_fk == 4:
                attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name,
                                        'slug': dat.type_name.replace(" ", "_"), 'selection_list': selection_list, 'value': ""})
            else:
                attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name,
                                        'slug': dat.type_name.replace(" ", "_"), 'value': ""})


    data = {
        'document': document.document,
        'name': document.name,
        'description': document.description,
        'created': document.created.isoformat(),
        'creator': document.creator,
        'updated': document.updated.isoformat() if document.updated else "",
        'updater': document.updater,
        'status': document.doc_status_type_fk,
        'statuses': statuses_list,
        'type': doc_type.type_name,
        'catalog': catalog.name,
        'catalog_id': catalog.doc_catalog,
        'attributes': attributes_list
    }

    if request.is_ajax():
        data['csrf_token'] = django.middleware.csrf.get_token(request)
        return HttpResponse(json.dumps(data))

@must_be_logged_in
def get_new_document_form(request, id):
    types = DocType.objects.all()
    types_list = []
    for type in types:
        types_list.append({'key': type.doc_type, 'value': type.type_name})

    categories = DocCatalog.objects.all()
    categories_list = []
    for category in categories:
        categories_list.append({'key': category.doc_catalog, 'value': category.name})

    statuses = DocStatusType.objects.all()
    statuses_list = []
    for selection in statuses:
        statuses_list.append({'key': selection.doc_status_type, 'value': selection.type_name})


    doc_type_attributes = DocTypeAttribute.objects.filter(doc_type_fk=id).order_by('orderby')
    doc_attribute_types = DocAttributeType.objects.filter(doc_attribute_type__in=[dta.doc_attribute_type_fk for dta in doc_type_attributes])

    attributes_list = []
    for dat in doc_attribute_types:

        # If input is a dropdown box:
        if dat.data_type_fk == 4:
            selection_values = AtrTypeSelectionValue.objects.filter(doc_attribute_type_fk=dat.doc_attribute_type).order_by('orderby')
            selection_list = []
            for selection in selection_values:
                selection_list.append({'key': selection.atr_type_selection_value, 'value': selection.value_text})

        # If input is a dropdown box:
        if dat.data_type_fk == 4:
            attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name, 'slug': dat.type_name.replace(" ", "_"), 'selection_list': selection_list, 'value': ""})
        else:
            attributes_list.append({'id': dat.doc_attribute_type, 'type': dat.data_type_fk, 'name': dat.type_name, 'slug': dat.type_name.replace(" ", "_"), 'value': ""})

    data = {
        'types': types_list,
        'categories': categories_list,
        'statuses': statuses_list,
        'attributes': attributes_list
    }

    if request.is_ajax():
        data['csrf_token'] = django.middleware.csrf.get_token(request)
        return HttpResponse(json.dumps(data))

@must_be_logged_in
def save_document(request, id):
    import pprint
    pprint.pprint(json.loads(request.body))
    post_values = json.loads(request.body)
    for attr in post_values['attributes']:
        post_values[attr['name'].replace(" ", "_")] = attr['value']
    # pprint.pprint(post_values)
    if post_values['type'] == "teabenoue" or post_values['type'] == 10:
        form = TeabenoueForm(post_values)
    elif post_values['type'] == "tooleping" or post_values['type'] == 9:
        form = ToolepingForm(post_values)
    elif post_values['type'] == "yyrileping" or post_values['type'] == 8:
        form = YyrilepingForm(post_values)
    elif post_values['type'] == "tarneleping" or post_values['type'] == 7:
        form = TarnelepingForm(post_values)
    else:
        form = DocumentForm(post_values)

    if form.is_valid():
        document = Document.objects.get(document=id)
        document.name = form.cleaned_data['name']
        document.description = form.cleaned_data['description']
        document.doc_status_type_fk = form.cleaned_data['status']
        document.updated_by = request.session.get('user')['emp']
        document.save()
        form.doc_save(document, post_values)
        c = connection.cursor()
        try:
            c.execute("BEGIN")
            c.callproc("edit_document_doc_catalog", (document.document, post_values['catalog_id'], request.session.get('user')['emp']))
            c.execute("COMMIT")
        finally:
            c.close()
        return JsonResponse({'status': "OK"})
    else:
        return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json')

@must_be_logged_in
def save_new_document(request):
    import pprint
    pprint.pprint(json.loads(request.body))
    post_values = json.loads(request.body)
    for attr in post_values['attributes']:
        post_values[attr['name'].replace(" ", "_")] = attr['value']
    # pprint.pprint(post_values)
    if post_values['type'] == "teabenoue" or post_values['type'] == 10:
        form = TeabenoueForm(post_values)
    elif post_values['type'] == "tooleping" or post_values['type'] == 9:
        form = ToolepingForm(post_values)
    elif post_values['type'] == "yyrileping" or post_values['type'] == 8:
        form = YyrilepingForm(post_values)
    elif post_values['type'] == "tarneleping" or post_values['type'] == 7:
        form = TarnelepingForm(post_values)
    else:
        form = DocumentForm(post_values)

    if form.is_valid():
        document = Document()
        document.name = form.cleaned_data['name']
        document.description = form.cleaned_data['description']
        document.doc_status_type_fk = form.cleaned_data['status']
        document.created = datetime.datetime.now()
        document.created_by = request.session.get('user')['emp']
        document.save()
        print document.document
        form.doc_save(document, post_values)
        c = connection.cursor()
        try:
            c.execute("BEGIN")
            c.callproc("edit_document_doc_catalog", (document.document, post_values['category'], request.session.get('user')['emp']))
            c.execute("COMMIT")
        finally:
            c.close()
        return redirect('dokud.views.documents_list')
    else:
        return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json')

@require_http_methods(["DELETE"])
@must_be_logged_in
def delete_document(request, id):
    try:
        document = Document.objects.get(document=id)
        document.delete()
        doc_attribute = DocAttribute.objects.filter(document_fk=id).delete()
        doc_status = DocStatus.objects.filter(document_fk=id).delete()
        document_doc_catalog = DocumentDocCatalog.objects.get(document_fk=id)
        catalog = document_doc_catalog.doc_catalog_fk
        document_doc_catalog.delete()
        doc_subject = DocSubject.objects.filter(document_fk=id).delete()

        doc_catalog = DocCatalog.objects.get(doc_catalog=catalog)
        doc_catalog.content_updated = datetime.datetime.now()
        doc_catalog.content_updated_by = request.session.get('user')['emp']
        doc_catalog.save()
        return JsonResponse({'status': "OK"})
    except:
        return JsonResponse({'status': "NOK"})