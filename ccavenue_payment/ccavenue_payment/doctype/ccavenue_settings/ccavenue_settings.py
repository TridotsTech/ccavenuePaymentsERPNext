# -*- coding: utf-8 -*-
# Copyright (c) 2019, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.utils import get_url
from six.moves.urllib.parse import urlencode
from frappe.integrations.utils import create_payment_gateway


class CCAvenueSettings(Document):
	supported_currencies = [
		 "CAD", "USD","INR"
	]
	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(_("Please select another payment method. Moneris does not support transactions in currency '{0}'").format(currency))
	def get_payment_url(self, **kwargs):
		return get_url("./ccavenue_checkout?{0}".format(urlencode(kwargs)))
	def on_update(self):
		if not frappe.db.exists("Account", "CCAvenue - TT"):
			account = frappe.get_doc({
				"doctype": "Account",
				"account_name":"CCAvenue",
				"root_type": "Asset",
				"report_type": "Balance Sheet",
				"parent_account": "Bank Accounts - TT",
				"account_type":"Bank"
			})
			account.insert(ignore_permissions=True)
		account=frappe.get_doc("Account","CCAvenue - TT")
		create_payment_gateway('CCAvenue','CCAvenue Settings')
		if not frappe.db.get_all("Payment Gateway Account", filters={"payment_gateway":"CCAvenue"}):
			payment_account = frappe.get_doc({
				"doctype": "Payment Gateway Account",
				"payment_gateway":"CCAvenue",
				"payment_account":account.name,
				"currency":account.account_currency
			})
			payment_account.insert(ignore_permissions=True)

def get_gateway_controller(doctype, docname):
	reference_doc = frappe.get_doc(doctype, docname)
	gateway_controller = frappe.db.get_value("Payment Gateway", reference_doc.payment_gateway, "gateway_controller")
	return gateway_controller


@frappe.whitelist(allow_guest=True)
def ccavenue_request_payment(payment_info):
	from ccavenue_payment.ccavenue_payment.ccavutil import encrypt,decrypt
	from string import Template
	request=json.loads(payment_info)
	gateway_settings=frappe.get_single('CCAvenue Settings')
	p_merchant_id = request.get('merchant_id')
	p_order_id = request.get('order_id')
	p_currency = request.get('currency')
	p_amount = request.get('amount')
	p_redirect_url = request.get('redirect_url')
	p_cancel_url = request.get('cancel_url')
	p_language = request.get('language')
	p_billing_name = request.get('billing_name')
	p_billing_address = request.get('billing_address')
	p_billing_city = request.get('billing_city')
	p_billing_state = request.get('billing_state')
	p_billing_zip = request.get('billing_zip')
	p_billing_country = request.get('billing_country')
	p_billing_tel = request.get('billing_tel')
	p_billing_email = request.get('billing_email')
	p_delivery_name = request.get('delivery_name')
	p_delivery_address = request.get('delivery_address')
	p_delivery_city = request.get('delivery_city')
	p_delivery_state = request.get('delivery_state')
	p_delivery_zip = request.get('delivery_zip')
	p_delivery_country = request.get('delivery_country')
	p_delivery_tel = request.get('delivery_tel')
	p_merchant_param1 = request.get('merchant_param1')
	p_merchant_param2 = request.get('merchant_param2')
	p_merchant_param3 = request.get('merchant_param3')
	p_merchant_param4 = request.get('merchant_param4')
	p_merchant_param5 = request.get('merchant_param5')
 	p_promo_code = request.get('promo_code')
	p_customer_identifier = request.get('customer_identifier')
	accessCode = gateway_settings.access_code 	
	workingKey = gateway_settings.working_key
	merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
	encryption = encrypt(merchant_data,workingKey)
	html = '''\
	 
			<input type="hidden" id="encRequest" name="encRequest" value=$encReq>
			<input type="hidden" name="access_code" id="access_code" value=$xscode>
			 
	 
	'''
	fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)
			
	return fin