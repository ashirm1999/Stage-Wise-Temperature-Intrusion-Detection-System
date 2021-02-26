import conf
from boltiot import Sms, Bolt, Email
import json, time
from datetime import datetime
import pytz

L = []
mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL, conf.SENDER_EMAIL, conf.RECIPIENT_EMAIL)

def Average(L):
        return sum(L) / len(L)
def buzzeron():
        output = mybolt.analogWrite('0','100');
        return output

def buzzon():
        output = mybolt.analogWrite('0','255');
        return output
def buzzeroff():
        output = mybolt.digitalWrite("0","LOW")
        return output

while True:
        response = mybolt.analogRead('A0')
        data = json.loads(response)
        try:

                sensor_value = int(data['value'])
                T = sensor_value/10.24
                print("The Tempreture inside is : " ,T)
                L.append(T)
                average = Average(L)
                if( len(L) >= 2 ):
                        if( (T > (average + 0.20)) and (T < (average + 0.30)) ):
                                print("STAGE 01 ANOMALY : " , T)
                                print("Making request to Mailgun to send email")
                                response = mailer.send_email("Alert", "Looks like door of Refrigerator is open Please close the door"  + str(T) )
                                response_text = json.loads(response.text)
                                print("Response received from MAILGUN is : " + str(response_text['message']))
                                buzzeron()
                                time.sleep(5)
                                buzzeroff()
                                tz_IN = pytz.timezone('Asia/Kolkata')
				datetime_IN = datetime.now(tz_IN)
                                print("Door is Open since :", datetime_IN.strftime("%H:%M:%S"))
                                break
                        elif( (T > (average + 0.30  )) ):
                                print("STAGE 02 ANOMALY  : " , T)
                                print("Making request to Twilio to send SMS")
                                response = sms.send_sms("Someone Has Opened the Door: " +str(T))
                                print("Response received from Twilio : " +str(response))
                                print("Status of SMS at Twilio : " +str(response.status))
                                buzzon()
                                time.sleep(5)
                                buzzeroff()
                                tz_IN = pytz.timezone('Asia/Kolkata')
                                datetime_IN = datetime.now(tz_IN)
                                print("Someone Opened the door at : " , datetime_IN.strftime("%H:%M:%S"))
                                break
        except Exception as e:
                print(e)
        time.sleep(1)
