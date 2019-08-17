
from __future__ import unicode_literals
# import frappe
# from _future_ import unicode_literals
import frappe
import frappe.utils
import ccavenue_payment
from frappe import _
from frappe.utils import fmt_money
from ccavenue_payment.ccavenue_payment.doctype.ccavenue_settings.ccavenue_settings import get_gateway_controller

no_cache = 1
no_sitemap = 1

expected_keys = ('amount', 'title', 'description', 'reference_doctype', 'reference_docname',
	'payer_name', 'payer_email', 'order_id', 'currency')

def get_context(context):
	try:
		context.no_cache = 1
		# all these keys exist in form_dict
		if not (set(expected_keys) - set(list(frappe.form_dict))):
			for key in expected_keys:
				context[key] = frappe.form_dict[key]
			if frappe.form_dict['payer_email']:
				if frappe.form_dict['payer_email']!=frappe.session.user:
					frappe.throw(_("Not permitted"), frappe.PermissionError)
			else:
				frappe.redirect_to_message(_('Some information is missing'),
				_('Looks like someone sent you to an incomplete URL. Please ask them to look into it.'))
				frappe.local.flags.redirect_location = frappe.local.response.location
				raise frappe.Redirect
			context.reference_docname=frappe.form_dict['order_id']
			gateway_controller = get_gateway_controller(context.reference_doctype, context.reference_docname)
			context['amount'] = fmt_money(amount=context['amount'], currency=context['currency'])
			payment_request=frappe.get_doc("Payment Request",frappe.form_dict['order_id'])
			sale_order=frappe.get_doc("Sales Order",payment_request.reference_name)
			context.sale_order=sale_order
			gateway_settings=frappe.get_single('CCAvenue Settings')
			context.gateway_settings=gateway_settings
			billing_info=frappe.get_doc("Address", sale_order.customer_address)
			shipping_info=frappe.get_doc("Address", sale_order.shipping_address_name)
			context.billing_info=billing_info
			context.shipping_info=shipping_info
			if frappe.db.get_value(context.reference_doctype, context.reference_docname, "is_a_subscription"):
				payment_plan = frappe.db.get_value(context.reference_doctype, context.reference_docname, "payment_plan")
				recurrence = frappe.db.get_value("Payment Plan", payment_plan, "recurrence")
				context['amount'] = context['amount'] + " " + _(recurrence)
		else:
			frappe.redirect_to_message(_('Some information is missing'),
				_('Looks like someone sent you to an incomplete URL. Please ask them to look into it.'))
			frappe.local.flags.redirect_location = frappe.local.response.location
			raise frappe.Redirect

	except Exception as e:
			frappe.log_error(frappe.get_traceback(), "ccavenue_payment.ccavenue_payment.templates.pages.ccavenue_checkout.get_context")
			frappe.redirect_to_message(_('Some information is missing'),
				_('Looks like someone sent you to an incomplete URL. Please ask them to look into it.'))
			frappe.local.flags.redirect_location = frappe.local.response.location
			raise frappe.Redirect