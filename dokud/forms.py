# coding=utf-8
from datetime import datetime
from decimal import Decimal
from django import forms
from dokud.models import DocAttribute, DocTypeAttribute, DocumentDocType


class DocumentForm(forms.Form):
    name = forms.CharField(min_length=5, error_messages={'required': 'See väli on kohustuslik.', 'min_length': 'See väli peab vähemalt 5 tähemärgi pikkune olema.'})
    description = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    status = forms.IntegerField(error_messages={'required': 'See väli on kohustuslik.'})

    def doc_save(self, document, post_values):
        ddt, ddt_created = DocumentDocType.objects.get_or_create(document_fk=document.document)
        if ddt_created:
            ddt.doc_type_fk = post_values['type']
            ddt.save()
        for attr in post_values['attributes']:
            da = DocAttribute.objects.filter(doc_attribute_type_fk=attr['id'], document_fk=document.document).first()
            if not da:
                last_da = DocAttribute.objects.last()
                da = DocAttribute(doc_attribute=(last_da.doc_attribute + 1), doc_attribute_type_fk=attr['id'])
            if attr['type'] == 1:
                da.value_text = attr['value']
            elif attr['type'] == 2:
                da.value_number = Decimal(attr['value'] or 0) if attr['value'] else None
            elif attr['type'] == 3:
                da.value_date = datetime.strptime(attr['value'], "%d.%m.%Y") if attr['value'] else None
            elif attr['type'] == 4:
                da.atr_type_selection_value_fk = Decimal(attr['value'] or 0)
            da.document_fk = document.document
            da.type_name = attr['name']
            da.data_type = attr['type']

            dta = DocTypeAttribute.objects.get(doc_attribute_type_fk=attr['id'], doc_type_fk=ddt.doc_type_fk)
            da.orderby = dta.orderby
            da.required = dta.required
            da.save()

class TarnelepingForm(DocumentForm):
    Lepingu_tyyp = forms.IntegerField(error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_algus = forms.DateField(input_formats=['%d.%m.%Y'], error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_lopp = forms.DateField(required=False, input_formats=['%d.%m.%Y'], error_messages={'invalid': 'Selles väljas peab olema kuupäev.'})
    Tasu = forms.FloatField(min_value=0, error_messages={'required': 'See väli on kohustuslik.', 'invalid': 'Selles väljas peab olema number.', 'min_value': 'Väärtus peab olema suurem kui 0.'})
    Tellija = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    Tarnija = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})

class YyrilepingForm(DocumentForm):
    Lepingu_tyyp = forms.IntegerField(error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_algus = forms.DateField(input_formats=['%d.%m.%Y'], error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_lopp = forms.DateField(required=False, input_formats=['%d.%m.%Y'], error_messages={'invalid': 'Selles väljas peab olema kuupäev.'})
    Tasu = forms.FloatField(min_value=0, error_messages={'required': 'See väli on kohustuslik.', 'invalid': 'Selles väljas peab olema number.', 'min_value': 'Väärtus peab olema suurem kui 0.'})
    Yyrileandja = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    Yyrilevotja = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})

class ToolepingForm(DocumentForm):
    Lepingu_tyyp = forms.IntegerField(error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_algus = forms.DateField(input_formats=['%d.%m.%Y'], error_messages={'required': 'See väli on kohustuslik.'})
    Lepingu_lopp = forms.DateField(required=False, input_formats=['%d.%m.%Y'], error_messages={'invalid': 'Selles väljas peab olema kuupäev.'})
    Tasu = forms.FloatField(min_value=0, error_messages={'required': 'See väli on kohustuslik.', 'invalid': 'Selles väljas peab olema number.', 'min_value': 'Väärtus peab olema suurem kui 0.'})
    Tootaja_nimi = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    Tooandja_nimi = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    Ettevotte_esindaja = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})
    Ametinimetus = forms.CharField(error_messages={'required': 'See väli on kohustuslik.'})

class TeabenoueForm(DocumentForm):
    saatjad = forms.CharField(required=False)
    vastamise_tahtaeg = forms.IntegerField(error_messages={'required': 'See väli on kohustuslik.'})
    formaat = forms.CharField(required=False)
    Telefoninumber = forms.IntegerField(required=False, min_value=1000000, error_messages={'required': 'See väli on kohustuslik.', 'invalid': 'Selles väljas peab olema number.', 'min_value': 'Väärtus peab olema vähemalt seitsmekohaline.'})
    Meiliaadress = forms.EmailField(error_messages={'required': 'See väli on kohustuslik.', 'invalid': 'Selles väljas peab olema meiliaadress.'})