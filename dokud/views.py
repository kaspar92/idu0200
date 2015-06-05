from django.shortcuts import render, get_object_or_404

# Create your views here.
from dokud.models import Document, DocType, DocumentDocType, DocCatalog, DocumentDocCatalog


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
        'documents': documents
    }

    return render(request, 'documents.html', data)

def catalog_list(request, catalog_name):
    catalog = get_object_or_404(DocCatalog, name=catalog_name.replace("-", " "))
    document_ids = [ddc.document_fk for ddc in DocumentDocCatalog.objects.filter(doc_catalog_fk=catalog.doc_catalog)]
    documents = Document.objects.filter(document__in=document_ids)

    data = {
        'documents': documents
    }

    return render(request, 'documents.html', data)