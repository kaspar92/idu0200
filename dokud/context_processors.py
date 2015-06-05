from dokud.models import DocType, DocCatalog


def sidebar(request):

    document_types = DocType.objects.filter(level=1)
    for doctype in document_types:
        subtypes = DocType.objects.filter(level=2, super_type_fk=doctype.doc_type)
        setattr(doctype, 'sub_types', subtypes)

    document_catalogs = DocCatalog.objects.filter(level=1)
    for catalog in document_catalogs:
        subcatalogs = DocCatalog.objects.filter(level=2, upper_catalog=catalog.doc_catalog)
        setattr(catalog, 'sub_catalogs', subcatalogs)

    data = {
        'document_types': document_types,
        'document_catalogs': document_catalogs
    }

    return data