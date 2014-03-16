
__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 by the individual contributors
  (see AUTHORS file)

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Contact information:
MIT Educational Studies Program
  84 Massachusetts Ave W20-467, Cambridge, MA 02139
  Phone: 617-253-4882
  Email: esp-webmasters@mit.edu
Learning Unlimited, Inc.
  527 Franklin St, Cambridge, MA 02139
  Phone: 617-379-0178
  Email: web-team@lists.learningu.org
"""
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, meets_deadline, main_call, aux_call
from esp.program.modules import module_ext
from esp.datatree.models import *
from esp.web.util        import render_to_response
from datetime            import datetime        
from django.db.models.query     import Q
from django.http         import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from esp.users.models    import ESPUser
from esp.accounting.controllers import ProgramAccountingController, IndividualAccountingController
from esp.middleware      import ESPError
from esp.middleware.threadlocalrequest import get_current_request

from django.conf import settings

from decimal import Decimal
import stripe
import re

class CreditCardModule_FirstData(ProgramModuleObj, module_ext.StripeCreditCardSettings):
    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Credit Card Payment Module (First Data)",
            "link_title": "Credit Card Payment",
            "module_type": "learn",
            "seq": 10000,
            }

    def isCompleted(self):
        """ Whether the user has paid for this program or its parent program. """
        return IndividualAccountingController(self.program, get_current_request().user).has_paid()
    have_paid = isCompleted

    def students(self, QObject = False):
        #   This query represented students who have a payment transfer from the outside
        pac = ProgramAccountingController(self.program)
        QObj = Q(transfer__source__isnull=True, transfer__line_item=pac.default_payments_lineitemtype())

        if QObject:
            return {'creditcard': QObj}
        else:
            return {'creditcard':ESPUser.objects.filter(QObj).distinct()}

    def studentDesc(self):
        return {'creditcard': """Students who have filled out the credit card form."""}

    @aux_call
    def payment_success(self, request, tl, one, two, module, extra, prog):
        """ Receive payment from First Data Global Gateway """

        if request.method == 'GET' or request.POST.get('status', '') != 'APPROVED':
            return self.payment_failure(request, tl, one, two, module, extra, prog)

        #   We should already know what user/program this is for, but it should also be stored.
        iac = IndividualAccountingController(self.program, request.user)
        post_locator = request.POST.get('ponumber', '')
        assert(post_locator == iac.get_id())

        post_identifier = request.POST.get('invoice_number', '')
        #   Optional: The line of code below would check consistency of the user's
        #   invoice items against the ones associated with the payment.
        #   assert(post_identifier == iac.get_identifier())

        post_amount = Decimal(request.POST.get('total', '0.0'))

        #   Warn for possible duplicate payments
        prev_payments = iac.get_transfers().filter(line_item=iac.default_payments_lineitemtype())
        if prev_payments.count() > 0 and iac.amount_due() <= 0:
            from django.conf import settings
            recipient_list = [contact[1] for contact in settings.ADMINS]

            subject = 'Possible Duplicate Postback/Payment'
            refs = 'User: %s (%d); Program: %s (%d)' % (request.user.name(), request.user.id, self.program.niceName(), self.program.id)
            refs += '\n\nPrevious payments\' Transfer IDs: ' + ( u', '.join([x.id for x in prev_payments]) )

            # Send mail!
            send_mail('[ ESP CC ] ' + subject + ' by ' + invoice.user.first_name + ' ' + invoice.user.last_name, \
                  """%s Notification\n--------------------------------- \n\n%s\n\nUser: %s %s (%s)\n\nCardholder: %s\n\nRequest: %s\n\n""" % \
                  (subject, refs, request.user.first_name, request.user.last_name, request.user.id, request.POST.get('bname', '--'), request) , \
                  settings.SERVER_EMAIL, recipient_list, True)

        #   Save the payment as a transfer in the database
        iac.submit_payment(post_amount)

        context = {}
        context['postdata'] = request.POST.copy()
        context['support_email'] = settings.DEFAULT_EMAIL_ADDRESSES['support']
        context['prog'] = prog

        #   Don't redirect to receipt just yet, in case they haven't finished all steps of registration
        #   return HttpResponseRedirect("http://%s/learn/%s/%s/confirmreg" % (request.META['HTTP_HOST'], one, two))
        return render_to_response(self.baseDir() + 'success.html', request, context)
        
    @aux_call
    def payment_failure(self, request, tl, one, two, module, extra, prog):
        context = {}
        if request.method == 'POST':
            context['postdata'] = request.POST.copy()
        context['prog'] = prog
        context['support_email'] = settings.DEFAULT_EMAIL_ADDRESSES['support']
        return render_to_response(self.baseDir() + 'failure.html', request, context)

    def check_setup(self):
        """ Validate the keys specified in the StripeCreditCardSettings object.
            If something is wrong, provide an error message which will hopefully
            only be seen by admins during setup. """

        #   A Stripe account comes with 4 keys, starting with e.g. sk_test_
        #   and followed by a 24 character base64-encoded string.
        valid_pk_re = r'pk_(test|live)_([A-Za-z0-9+/=]){24}'
        valid_sk_re = r'sk_(test|live)_([A-Za-z0-9+/=]){24}'
        config_url = '/admin/modules/stripecreditcardsettings/%d' % self.extension_id
        if not re.match(valid_pk_re, self.publishable_key) or not re.match(valid_sk_re, self.secret_key):
            raise ESPError('The site has not yet been properly set up for credit card payments.  Administrators should <a href="%s">configure payments here</a>.' % config_url, True)

    @main_call
    @usercheck_usetl
    @meets_deadline('/Payment')
    def payonline(self, request, tl, one, two, module, extra, prog):

        #   Check for setup of module.
        self.check_setup()

        user = ESPUser(request.user)

        iac = IndividualAccountingController(self.program, request.user)
        context = {}
        context['module'] = self
        context['program'] = prog
        context['user'] = user
        context['invoice_id'] = iac.get_id()
        context['identifier'] = iac.get_identifier()
        payment_type = iac.default_payments_lineitemtype()
        sibling_type = iac.default_siblingdiscount_lineitemtype()
        grant_type = iac.default_finaid_lineitemtype()
        context['itemizedcosts'] = iac.get_transfers().exclude(line_item__in=[payment_type, sibling_type, grant_type]).order_by('-line_item__required')
        context['itemizedcosttotal'] = iac.amount_due()
        context['totalcost_cents'] = int(context['itemizedcosttotal'] * 100)
        context['subtotal'] = iac.amount_requested()
        context['financial_aid'] = iac.amount_finaid()
        context['sibling_discount'] = iac.amount_siblingdiscount()
        context['amount_paid'] = iac.amount_paid()

        if 'HTTP_HOST' in request.META:
            context['hostname'] = request.META['HTTP_HOST']
        else:
            context['hostname'] = Site.objects.get_current().domain
        context['institution'] = settings.INSTITUTION_NAME
        context['support_email'] = settings.DEFAULT_EMAIL_ADDRESSES['support']
        
        return render_to_response(self.baseDir() + 'cardpay.html', request, context)

    @aux_call
    def charge_payment(self, request, tl, one, two, module, extra, prog):
        context = {'postdata': request.POST.copy()}

        #   Set Stripe key based on settings
        stripe.api_key = self.secret_key

        # Create the charge on Stripe's servers - this will charge the user's card 
        try: 
            charge = stripe.Charge.create(
                amount=int(request.POST['totalcost_cents']),
                currency="usd",
                card=request.POST['stripeToken'],
                description="Payment for %s - %s" % (prog.niceName(), request.user.name()),
            ) 
        except stripe.CardError, e:
            #   Handle declined card.
            return render_to_response(self.baseDir() + 'failure.html', request, context)
        except stripe.InvalidRequestError, e:
            #   Handle duplicate request
            return render_to_response(self.baseDir() + 'failure.html', request, context)

        return render_to_response(self.baseDir() + 'success_new.html', request, context)

    class Meta:
        abstract = True

