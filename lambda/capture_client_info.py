import apl_utils
import utils
from utils import get_token
from utils import call_safra_api
from utils import sms_controller
from utils import token_controller
from utils import authentication_controller
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor
)

class CaptureCPFIntentHandler(AbstractRequestHandler):
    """Handler for CPF Intent."""
    def can_handle(self, handler_input):
        return is_intent_name("CaptureCPFIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        cpf_one = slots["cpf_one"].value
        cpf_two = slots["cpf_two"].value
        cpf_three = slots["cpf_three"].value
        cpf_four = slots["cpf_four"].value
        cpf_five = slots["cpf_five"].value
        cpf_six = slots["cpf_six"].value
        cpf_seven = slots["cpf_seven"].value
        cpf_eight = slots["cpf_eight"].value
        cpf_nine = slots["cpf_nine"].value
        cpf_ten = slots["cpf_ten"].value
        cpf_eleven = slots["cpf_eleven"].value
        cpf = str(cpf_one) + str(cpf_two) + str(cpf_three) + \
            str(cpf_four) + str(cpf_five) + str(cpf_six) + \
            str(cpf_seven) + str(cpf_eight) + str(cpf_nine) + \
            str(cpf_ten) + str(cpf_eleven)

        attributes_manager = handler_input.attributes_manager
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        # Add cpf variable to session attributes
        session_attr["cpf"] = cpf
        
        speak_output = 'Thanks, I\'ll remember that your <say-as interpret-as="spell-out">CPF</say-as> is <say-as interpret-as="digits">{cpf}</say-as>. What\'s your celphone number?'.format(cpf=cpf)
        reprompt_text = 'What\'s your celphone number?'
        
        # Add APL Template if device is compatible
        apl_utils.capture_cpf_intent_screen(handler_input)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class CaptureCelphoneIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CaptureCelphoneIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        celphone_area_one = slots["celphone_area_one"].value
        celphone_area_two = slots["celphone_area_two"].value
        celphone_digit = slots["celphone_digit"].value
        celphone_number_one = slots["celphone_number_one"].value
        celphone_number_two = slots["celphone_number_two"].value
        celphone_number_three = slots["celphone_number_three"].value
        celphone_number_four = slots["celphone_number_four"].value
        celphone_number_five = slots["celphone_number_five"].value
        celphone_number_six = slots["celphone_number_six"].value
        celphone_number_seven = slots["celphone_number_seven"].value
        celphone_number_eight = slots["celphone_number_eight"].value
        celphone = "(" + str(celphone_area_one) + str(celphone_area_two) + ")" + str(celphone_digit) + \
            str(celphone_number_one) + str(celphone_number_two) + str(celphone_number_three) + str(celphone_number_four) + "-" + \
            str(celphone_number_five) + str(celphone_number_six) + str(celphone_number_seven) + str(celphone_number_eight)
        
        attributes_manager = handler_input.attributes_manager
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        # Add celphone variable to session attributes
        session_attr["celphone"] = celphone
        
        speak_output = 'Thanks, I will remember that your celphone is {celphone}. What\'s your account number?'.format(celphone=celphone)
        reprompt_text = 'What\'s your account number?'
        
        # Add APL Template if device is compatible
        apl_utils.capture_celphone_intent_screen(handler_input)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class CaptureAccountIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CaptureAccountIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        account_number = slots["account_number"].value
        
        attributes_manager = handler_input.attributes_manager
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        # Add account_number variable to session attributes
        session_attr["account_number"] = account_number
        
        # Adding session variables variables to persisted attributes
        persisted_attributes = {
            "cpf": session_attr["cpf"],
            "celphone": session_attr["celphone"],
            "account_number": session_attr["account_number"]
        }
        
        attributes_manager.persistent_attributes = persisted_attributes
        
        # Save persisted attributes
        attributes_manager.save_persistent_attributes()
        
        get_token = sms_controller(session_attr["cpf"])
        
        if (get_token == 200) : 
            speak_output = 'Thanks, I\'ll remember that your account number is <say-as interpret-as=\"digits\">{account_number}</say-as>. \
                To access our services, please confirm the token that was sent to your celphone.'.format(account_number=account_number)
            reprompt_text = 'Please, confirm the token we sent to your celphone.'
            
            # Add APL Template if device is compatible
            apl_utils.capture_account_intent_screen(handler_input)
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(reprompt_text)
                    .response
            )
        else : 
            speak_output = 'Error while sending SMS Token. Exiting.'
            logger.error("Error calling token API: {}".format(get_token))
            return handler_input.response_builder.speak(speak_output).set_should_end_session(True).response 
