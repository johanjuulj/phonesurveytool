class AIT:
    def setup():
        return "AIT"
    

class SMSutility:
    #setup method
    def setup(service:str, uri:str, account:str, passw:str):
        if service == "AfricaIsTalking":
            aitClient = AIT.setup()
            

            return "You are now connected to Twilio"


        elif service == "Twilio":
            #twilioClient = Twilio()
            
            return "You are now connected to Twilio"
        else:
            return None

