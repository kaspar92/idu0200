"""Dokumendid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^logout/', 'dokud.views.logout'),
    url(r'^search/', 'dokud.views.search'),

    url(r'^documents/catalog/(?P<catalog_name>[-\w]+)/', 'dokud.views.catalog_list'),
    url(r'^documents/(?P<document_type>[-\w]+)/', 'dokud.views.documents_list'),
    url(r'^documents/', 'dokud.views.documents_list'),
    url(r'^document/save/(?P<id>[-\w]+)', 'dokud.views.save_document'),
    url(r'^document/save_new/', 'dokud.views.save_new_document'),
    url(r'^document/delete/(?P<id>[-\w]+)', 'dokud.views.delete_document'),
    url(r'^document/(?P<id>[-\w]+)', 'dokud.views.document'),
    url(r'^new_document/', 'dokud.views.new_document'),
    url(r'^new_document_form/(?P<id>[-\w]+)', 'dokud.views.get_new_document_form'),

    url(r'', 'dokud.views.login_view'),
]
