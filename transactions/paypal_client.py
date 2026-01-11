import requests
from django.conf import settings
import base64

class PayPalClient:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        
        if self.mode == "sandbox":
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"

    def get_access_token(self):
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            url, 
            headers=headers, 
            data=data, 
            auth=(self.client_id, self.client_secret)
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        return None

    def create_order(self, amount, currency="USD", return_url=None, cancel_url=None):
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                }
            }],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "user_action": "PAY_NOW"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        return None

    def capture_order(self, order_id):
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.post(url, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
        return None
