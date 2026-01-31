import requests
from JMCDonations import settings
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime


class MpesaClient:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.api_url = settings.MPESA_API_URL
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE

    def get_access_token(self):
        url = f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        )
        print(response.status_code, response.text)
        if response.status_code == 200:
            return response.json()["access_token"]
        return None

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to authenticate with Daraja API"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        print("Using Callback URL:", settings.MPESA_CALLBACK_URL)
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        url = f"{self.api_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def b2b_payment(
        self,
        amount,
        party_b,
        account_reference,
        remarks="Business Transfer",
        command_id="BusinessPayBill",
    ):
        """
        Initiates a B2B payment (Paybill to Paybill/Till).
        default command_id is 'BusinessPayBill'.
        """
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to authenticate with Daraja API"}

        # Security Credential generation is complex and requires a certificate.
        # For this implementation, we will assume the environment provides a pre-generated SecurityCredential
        # or we skip it if testing in Sandbox (Sandbox often uses a static one, or initiator password).
        # However, strictly speaking, B2B requires `SecurityCredential`.
        # We will use settings.MPESA_SECURITY_CREDENTIAL.

        security_credential = getattr(settings, "MPESA_SECURITY_CREDENTIAL", "DUMMY_CREDENTIAL")

        payload = {
            "Initiator": getattr(settings, "MPESA_INITIATOR_NAME", "testapi"),
            "SecurityCredential": security_credential,
            "CommandID": command_id,
            "SenderIdentifierType": "4",  # 4 for Shortcode
            "RecieverIdentifierType": "4", # 4 for Shortcode
            "Amount": amount,
            "PartyA": self.shortcode,  # Source Paybill (150770)
            "PartyB": party_b,  # Destination Paybill
            "Remarks": remarks,
            "QueueTimeOutURL": settings.MPESA_CALLBACK_URL,
            "ResultURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        url = f"{self.api_url}/mpesa/b2b/v1/paymentrequest"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
