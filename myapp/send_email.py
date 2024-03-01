import  random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from . models import *
from .models import *
def send_otp(request, user_email, username):


    # Generate a random 6-digit OTP
    otp = str(random.randint(100000, 999999))


    # Get the current time
    now = timezone.now()

    # Set the expiry time (e.g., 5 minutes from the current time)
    expiry_time = now + timedelta(minutes=1)

    # Format the expiry_time as a human-readable string
    expiry_time_str = expiry_time.strftime("%B %d, %Y %I:%M %p")

    scheme = request.scheme  # http or https
    host = request.META['HTTP_HOST']  
    # Send the OTP to the user via email
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}\n Click Here to verify your otp link ----->  {scheme}://{host}/verify_otp/api'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    # store it into db
    # user = User.objects.get(email=user_email)

    try:
        otp_record = OTP_COLLECTION_db.objects.get(email=user_email)
        # Update the existing OTP record
        otp_record += 1
        otp_record.otp = otp
        otp_record.expireTime = expiry_time
        otp_record.save()
    except OTP_COLLECTION_db.DoesNotExist:
        # Create a new OTP record if it doesn't exist
        otp_record = OTP_COLLECTION_db(email=user_email, username=username, otp=otp, expireTime=expiry_time)
        otp_record.save()
