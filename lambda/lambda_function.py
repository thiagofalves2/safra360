# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os
import requests
import calendar
from datetime import datetime
from pytz import timezone
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome to Safra App. What is your CPF?"
        # reprompt_text required to keep session open or set shouldEndSession to true
        reprompt_text = "What is your CPF?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class HasClientInfoLaunchRequestHandler(AbstractRequestHandler):
    """Handler for launch after we save user's CPF"""
    
    def can_handle(self, handler_input):
        # extract persistent attributes and check if they are all present
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("cpf" in attr and "celphone" in attr and "account_number" in attr)
        
        return attributes_are_present and ask_utils.is_request_type("LaunchRequest")(handler_input)
        
    def handle(self, handler_input):
        # Extract persistent attributes and check if they are all present
        attr = handler_input.attributes_manager.persistent_attributes
        persisted_cpf = attr['cpf']
        
        speak_output = 'Welcome back, your CPF is {persisted_cpf}. How can I help you today? You can go to Safra Pay or Banking. Which service do you want?'.format(persisted_cpf=persisted_cpf)
        reprompt_text = 'How can I help you today? You can go to Safra Pay or Banking. Which service do you want?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class BankingIntentHandler(AbstractRequestHandler):
    """Handler for Banking Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BankingIntent")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speak_output = 'Welcome to Safra Banking. You can choose between Account Data, Account Statement or Account Balance. Which service do you want?'
        reprompt_text = 'How can I help you today? You can choose between Account Data, Account Statement or Account Balance. Which service do you want?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class AccountIntentHandler(AbstractRequestHandler):
    """Handler for Account Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AccountIntent")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        service = slots["service"].value
        
        speak_output = 'Welcome to your Account. You chose the service: Account {service}'.format(service=service)
        
        # It will exit for now.
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

# Asks user for account info
#class AccountServicesIntentHandler(AbstractRequestHandler):
#    """Handler for Account Intent."""
#    def can_handle(self, handler_input):
#        # type: (HandlerInput) -> bool
#        return ask_utils.is_intent_name("AccountDataIntent")(handler_input)
#        
#    def handle(self, handler_input):
#        # type: (HandlerInput) -> Response

#class AccountDataIntentHandler(AbstractRequestHandler):
#    """Handler for Account Intent."""
#    def can_handle(self, handler_input):
#        # type: (HandlerInput) -> bool
#        return ask_utils.is_intent_name("AccountDataIntent")(handler_input)
#        
#    def handle(self, handler_input):
#        # type: (HandlerInput) -> Response
#        
#        speak_output = 'Welcome to your Account. You chose the service: Account {service}'.format(service=service)
#        
#        # It will exit for now.
#        return (
#            handler_input.response_builder
#                .speak(speak_output)
#                # .ask("add a reprompt if you want to keep the session open for the user to respond")
#                .response
#        )

class CaptureCPFIntentHandler(AbstractRequestHandler):
    """Handler for CPF Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureCPFIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        cpf = str(cpf_one) + str(cpf_two) + str(cpf_three) + "." + \
            str(cpf_four) + str(cpf_five) + str(cpf_six) + "." + \
            str(cpf_seven) + str(cpf_eight) + str(cpf_nine) + "-" + \
            str(cpf_ten) + str(cpf_eleven)

        attributes_manager = handler_input.attributes_manager
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        # Add cpf variable to session attributes
        session_attr["cpf"] = cpf
        
        speak_output = 'Thanks, I will remember that your CPF is {cpf}. What\'s your celphone number?'.format(cpf=cpf)
        reprompt_text = 'What\'s your celphone number?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class CaptureCelphoneIntentHandler(AbstractRequestHandler):
    """Handler for Celphone Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureCelphoneIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        
        # Add celphone variable to persisted attributes
        persisted_attributes = {
            "celphone": celphone
        }
        
        attributes_manager.persistent_attributes = persisted_attributes
        
        # Save persisted attributes
        attributes_manager.save_persistent_attributes()
        
        speak_output = 'Thanks, I will remember that your celphone is {celphone}. What\'s your account number?'.format(celphone=celphone)
        reprompt_text = 'What\'s your account number?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class CaptureAccountIntentHandler(AbstractRequestHandler):
    """Handler for Account Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureAccountIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        account_number = slots["account_number"].value
        
        attributes_manager = handler_input.attributes_manager
        
        # Add account_number variable to persisted attributes
        persisted_attributes = {
            "account_number": account_number
        }
        
        attributes_manager.persistent_attributes = persisted_attributes
        
        # Save persisted attributes
        attributes_manager.save_persistent_attributes()
        
        speak_output = 'Thanks, I will remember that your account number is {account_number}.'.format(account_number=account_number)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask(reprompt_text)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

# Builder to use storage
sb = CustomSkillBuilder(persistence_adapter=s3_adapter)
#sb = SkillBuilder()

sb.add_request_handler(HasClientInfoLaunchRequestHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BankingIntentHandler())
sb.add_request_handler(AccountIntentHandler())
sb.add_request_handler(CaptureCPFIntentHandler())
sb.add_request_handler(CaptureCelphoneIntentHandler())
sb.add_request_handler(CaptureAccountIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
