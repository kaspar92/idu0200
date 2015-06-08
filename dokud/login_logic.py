from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def must_be_logged_in(view_function):
    return MustBeLoggedIn(view_function)

class MustBeLoggedIn(object):
    def __init__( self, view_function):
        self.view_function = view_function

    def __call__( self, request, *args, **kwargs ):
        if not request.session.get('user_logged_in'):
            return HttpResponseRedirect(reverse('dokud.views.login_view'))
        return self.view_function( request, *args, **kwargs )