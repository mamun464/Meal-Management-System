from django.core.mail import EmailMessage
import os

class Util:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage (
                subject=data['subject'],
                body=data['body'],
                to=[data['to_email']]
            )
            email.send()
            return True  # Return True if email sent successfully
        except Exception as e:
            print(str(e))
            return False  # Return False if email sending fails