# -*- coding: utf-8 -*-
# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import json
import prompts
import apl_utils

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import StandardCard, Image
from ask_sdk_model import Response
from ask_sdk_s3.adapter import S3Adapter

import os
import requests
from requests import Request, Session

import utils
from utils import get_token
from utils import call_safra_api
from utils import sms_controller
from utils import token_controller
from utils import authentication_controller

import capture_client_info
from capture_client_info import CaptureCPFIntentHandler
from capture_client_info import CaptureCelphoneIntentHandler
from capture_client_info import CaptureAccountIntentHandler

s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

# Builder to use storage
sb = CustomSkillBuilder(persistence_adapter=s3_adapter)
#sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LaunchRequestIntentHandler(AbstractRequestHandler):
    """
    Handles LaunchRequest requests sent by Alexa
    Note: this type of request is sent when hte user invokes your skill without providing a specific intent
    """
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        
        logger.info('Data variable: {}'.format(data))

        # Get prompt and reprompt speech
        speak_output = data[prompts.WELCOME_MESSAGE].format(
            data[prompts.SKILL_NAME])
        reprompt_output = data[prompts.WELCOME_REPROMPT]
        
        # Add APL Template if device is compatible
        apl_utils.launch_request_intent_screen(handler_input)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
                .response
        )

class HasClientInfoLaunchRequestHandler(AbstractRequestHandler):
    """Handler for launch after we save user's info"""
    def can_handle(self, handler_input):
        # Retrive persisted attributes and check if they are all present
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("cpf" in attr and "celphone" in attr and "account_number" in attr)
        
        return attributes_are_present and is_request_type("LaunchRequest")(handler_input)
        
    def handle(self, handler_input):
        # Extract persistent attributes
        attr = handler_input.attributes_manager.persistent_attributes
        persisted_cpf = attr['cpf']
        persisted_celphone = attr['celphone']
        persisted_account_number = attr['account_number']
        
        get_token = sms_controller(persisted_cpf)
        
        if (get_token == 200) : 
            speak_output = 'Welcome back, your <say-as interpret-as=\"spell-out\">CPF</say-as> is <say-as interpret-as=\"digits\">{persisted_cpf}</say-as>, your celphone is <say-as interpret-as=\"digits\">{persisted_celphone}</say-as> \
                and your account is <say-as interpret-as=\"digits\">{persisted_account_number}</say-as>. \
                To access our services, please confirm the token that was sent to your celphone.'.format(persisted_cpf=persisted_cpf, persisted_celphone=persisted_celphone, persisted_account_number=persisted_account_number)
            reprompt_text = 'Please, confirm the token we sent to your celphone.'
            
            # Add APL Template if device is compatible
            apl_utils.has_client_info_intent_screen(handler_input)
            
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

class AuthenticationIntentHandler(AbstractRequestHandler):
    """Handler for Authentication Intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AuthenticationIntent")(handler_input)
        
    def handle(self, handler_input):
        # Extract persistent attributes
        attributes_manager=handler_input.attributes_manager
        
        attr = attributes_manager.persistent_attributes
        
        persisted_cpf = attr['cpf']
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        logger.info('Session Atts: {}'.format(session_attr))
        logger.info('Type Self: {}'.format(type(self)))
        logger.info('Session Atts: {}'.format(type(AuthenticationIntentHandler())))
        
        if (type(self) != type(AuthenticationIntentHandler())) :
            old_speak_output = session_attr["previous_speak_output"]
            speak_output = '{} What more can I help you with today? You can go to Safra Pay or Banking. Which service do you want?'.format(old_speak_output)
            reprompt_text = 'How can I help you today? You can go to Safra Pay or Banking. Which service do you want?'
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
            )
        
        slots = handler_input.request_envelope.request.intent.slots
        token_one = slots["token_one"].value
        token_two = slots["token_two"].value
        token_three = slots["token_three"].value
        token_four = slots["token_four"].value
        token = str(token_one) + str(token_two) + str(token_three) + str(token_four)
        
        token_validated = token_controller(persisted_cpf,token)
        
        if (token_validated == 202) :
            speak_output = 'Token succesfully validated. How can I help you today? You can go to Safra Pay or Banking. Which service do you want?' 
            reprompt_text = 'How can I help you today? You can go to Safra Pay or Banking. Which service do you want?'
            
            # Add APL Template if device is compatible
            apl_utils.authentication_intent_screen(handler_input)
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
            )
        else :
            speak_output = 'Incorrect Token. Exiting.'
            logger.error("Incorrect token: {}".format(token))
            return handler_input.response_builder.speak(speak_output).set_should_end_session(True).response

class BankingIntentHandler(AbstractRequestHandler):
    """Handler for Banking Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("BankingIntent")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speak_output = 'Welcome to Safra Banking. You can choose between Account Data, Account Statement or Account Balance. Which service do you want?'
        reprompt_text = 'How can I help you today? You can choose between Account Data, Account Statement or Account Balance. Which service do you want?'
        
        # Add APL Template if device is compatible
        apl_utils.banking_intent_screen(handler_input)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class SafraPayIntentHandler(AbstractRequestHandler):
    """Handler for Safra Pay Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SafraPayIntent")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speak_output = 'Welcome to Safra Pay. Here you can check your Sold Amount, Received Amount and Future Amount on a specific date. Please choose service and date.'
        reprompt_text = 'How can I help you today? You can choose between Sold Amount, Received Amount or Future Amount and a specific date. Please choose service and date.'
        
        # Add APL Template if device is compatible
        apl_utils.safrapay_intent_screen(handler_input)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class AccountIntentHandler(AbstractRequestHandler):
    """ Handler for Account Intent. """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AccountIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        service = slots["service"].value
        
        attributes_manager = handler_input.attributes_manager
        
        attr = attributes_manager.persistent_attributes
        persisted_account_number = attr['account_number']
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        logger.info("Account: {}".format(persisted_account_number))
        logger.info("Service: {}".format(service))
        
        if (service == "data") :
            response_safra = call_safra_api('', persisted_account_number)
            session_attr["data_response"] = response_safra
            
            if (response_safra == '') :
                logger.error("Empty API response.")
                return ''
            else : 
                # Get Data dict
                account_data = response_safra['Data']
                logger.info("Account Data: {}".format(account_data))
                
                # Get Account list
                account = account_data['Account']
                logger.info("Account: {}".format(account))
                
                # Get first account
                account_record = account[0]
                
                # Get first account data
                account_id = account_record['AccountId']
                logger.info("Account Id: {}".format(account_id))
                account_currency = account_record['Currency']
                logger.info("Account Currency: {}".format(account_currency))
                account_nickname = account_record['Nickname']
                account_info = account_record['Account']
                account_identification = account_info['Identification']
                account_name = account_info['Name']
                account_sec_id = account_info['SecondaryIdentification']
                account_link = response_safra['Links']['Self']
                
                speak_output = 'Your account data is:\nAccount ID: {account_id}\nCurrency: {account_currency}\nNickname: {account_nickname}\nIdentification: {account_identification}\n \
                    Name: {account_name}\nSecondary ID: {account_sec_id}\nLink: {account_link}.'.format(account_id=account_id,account_currency=account_currency,account_nickname=account_nickname, \
                    account_identification=account_identification,account_name=account_name,account_sec_id=account_sec_id,account_link=account_link)
                
                # Add speak_output variable to session attributes
                session_attr["previous_speak_output"] = speak_output
                
                # Add APL Template if device is compatible
                apl_utils.data_screen(handler_input)

        elif (service == "balance") :
            response_safra = call_safra_api('/balances', persisted_account_number)
            session_attr["balance_response"] = response_safra
            
            if (response_safra == '') :
                logger.error("Empty API response.")
                return ''
            else : 
                # Account data
                account_data = response_safra['Data']
                logger.info("Account Data: {}".format(account_data))
                
                balance = account_data['Balance']
                balance_record = balance[0]
                
                account_id = balance_record['AccountId']
                logger.info("Account Id: {}".format(account_id))
                
                amount_record = balance_record['Amount']
                
                amount = amount_record['Amount']
                logger.info("Balance Amount: {}".format(amount))
                
                currency = amount_record['Currency']
                logger.info("Balance Currency: {}".format(currency))
                
                credit_debit = balance_record['CreditDebitIndicator']
                logger.info("Credit/Debit: {}".format(credit_debit))
                
                balance_type = balance_record['Type']
                logger.info("Balance Type: {}".format(balance_type))
                
                balance_date = balance_record['DateTime']
                logger.info("Balance Date: {}".format(balance_date))
                
                balance_credit_line = balance_record['CreditLine']
                credit_line_record = balance_credit_line[0]
                
                credit_line_included = credit_line_record['Included']
                logger.info("Credit line included? {}".format(credit_line_included))
                
                credit_line_amount = credit_line_record['Amount']['Amount']
                logger.info("Credit Line Amount: {}".format(credit_line_amount))
                
                credit_currency = credit_line_record['Amount']['Currency']
                logger.info("Credit Line Currency: {}".format(credit_currency))
                
                credit_line_type = credit_line_record['Type']
                logger.info("Credit Line Type: {}".format(credit_line_type))
                
                account_link = response_safra['Links']['Self']
                
                speak_output = 'Your account balance is: \
                    Account ID: {account_id} \
                    Balance Amount: {amount} \
                    Balance Currency: {currency} \
                    Credit/Debit: {credit_debit} \
                    Balance Type: {balance_type} \
                    Balance Date: {balance_date} \
                    Credit Line Included? {credit_line_included} \
                    Credit Line Amount: {credit_line_amount} \
                    Credit Line Currency: {credit_currency} \
                    Credit Line Type: {credit_line_type} \
                    Link: {account_link}.'.format(account_id=account_id,amount=amount,currency=currency, \
                    credit_debit=credit_debit,balance_type=balance_type,balance_date=balance_date,credit_line_included=credit_line_included, \
                    credit_line_amount=credit_line_amount, credit_currency=credit_currency, credit_line_type=credit_line_type, account_link=account_link)
                    
                # Add speak_output variable to session attributes
                session_attr["previous_speak_output"] = speak_output
                
                # Add APL Template if device is compatible
                apl_utils.balance_screen(handler_input)

        else :
            response_safra = call_safra_api('/transactions', persisted_account_number)
            session_attr["transactions_response"] = response_safra

            # Account data
            account_data = response_safra['data']
            logger.info("Account Data: {}".format(account_data))
            
            transaction = account_data['transaction']
            transaction_record = transaction[0]
            
            account_id = transaction_record['accountId']
            logger.info("Account Id: {}".format(account_id))
            
            transaction_id = transaction_record['transactionId']
            logger.info("Transaction Id: {}".format(transaction_id))
            
            transaction_amount = transaction_record['amount']['amount']
            logger.info("Transaction Amount: {}".format(transaction_amount))
            
            transaction_currency = transaction_record['amount']['currency']
            logger.info("Transaction Currency: {}".format(transaction_currency))
            
            credit_debit = transaction_record['creditDebitIndicator']
            logger.info("Credit/Debit: {}".format(credit_debit))
            
            transaction_status = transaction_record['status']
            logger.info("Transaction Status: {}".format(transaction_status))
            
            transaction_booking_datetime = transaction_record['bookingDateTime']
            logger.info("Transaction Booking Date: {}".format(transaction_booking_datetime))
            
            transaction_value_datetime = transaction_record['valueDateTime']
            logger.info("Transaction Value Date: {}".format(transaction_value_datetime))
            
            transaction_info = transaction_record['transactionInformation']
            logger.info("Transaction Info: {}".format(transaction_info))
            
            bank_transaction_code = transaction_record['bankTransactionCode']['code']
            logger.info("Bank Transaction Code: {}".format(bank_transaction_code))
            
            bank_transaction_subcode = transaction_record['bankTransactionCode']['subCode']
            logger.info("Bank Transaction Subcode: {}".format(bank_transaction_subcode))
            
            proprietary_bank_transaction_code = transaction_record['proprietaryBankTransactionCode']['code']
            logger.info("Proprietary Bank Transaction Code: {}".format(proprietary_bank_transaction_code))
            
            proprietary_bank_transaction_issuer = transaction_record['proprietaryBankTransactionCode']['issuer']
            logger.info("Proprietary Bank Transaction Issuer: {}".format(proprietary_bank_transaction_issuer))
            
            transaction_balance_amount_record = transaction_record['balance']['amount']
            
            transaction_balance_amount = transaction_balance_amount_record['amount']
            logger.info("Transaction Balance Amount: {}".format(transaction_balance_amount))
            
            transaction_balance_currency = transaction_balance_amount_record['currency']
            logger.info("Transaction Balance Currency: {}".format(transaction_balance_currency))
            
            transaction_balance_creditdebit = transaction_record['balance']['creditDebitIndicator']
            logger.info("Transaction Balance Credit/Debit: {}".format(transaction_balance_creditdebit))
            
            transaction_balance_type = transaction_record['balance']['type']
            logger.info("Transaction Balance Type: {}".format(transaction_balance_type))
            
            account_link = response_safra['links']['self']

            speak_output = 'Here\'s your account transaction: \
                Account ID: {account_id} \
                Transaction ID: {transaction_id} \
                Transaction Amount: {transaction_amount} \
                Transaction Currency: {transaction_currency} \
                Transaction Credit/Debit: {credit_debit} \
                Transaction Status: {transaction_status} \
                Transaction Booking Date: {transaction_booking_datetime} \
                Transaction Value Date: {transaction_value_datetime} \
                Transaction Info: {transaction_info} \
                Bank Transaction Code: {bank_transaction_code} \
                Bank Transaction Subcode: {bank_transaction_subcode} \
                Proprietary Bank Transaction Code: {proprietary_bank_transaction_code} \
                Proprietary Bank Transaction Issuer: {proprietary_bank_transaction_issuer} \
                Transaction Balance Amount: {transaction_balance_amount} \
                Transaction Balance Currency: {transaction_balance_currency} \
                Transaction Balance Credit/Debit: {transaction_balance_creditdebit} \
                Transaction Balance Type: {transaction_balance_type} \
                Link: {account_link}.'.format(account_id=account_id, transaction_id=transaction_id, transaction_amount=transaction_amount, transaction_currency=transaction_currency, \
                credit_debit=credit_debit, transaction_status=transaction_status, transaction_booking_datetime=transaction_booking_datetime, transaction_value_datetime=transaction_value_datetime, \
                transaction_info=transaction_info, bank_transaction_code=bank_transaction_code, bank_transaction_subcode=bank_transaction_subcode, proprietary_bank_transaction_code=proprietary_bank_transaction_code, \
                proprietary_bank_transaction_issuer=proprietary_bank_transaction_issuer, transaction_balance_amount=transaction_balance_amount, transaction_balance_currency=transaction_balance_currency, \
                transaction_balance_creditdebit=transaction_balance_creditdebit, transaction_balance_type=transaction_balance_type, account_link=account_link)
                
            # Add speak_output variable to session attributes
            session_attr["previous_speak_output"] = speak_output
            
            # Add APL Template if device is compatible
            apl_utils.transactions_screen(handler_input)
        
        # Return to "menu".
        return AuthenticationIntentHandler.handle(self, handler_input)

class SafraPayAccountIntentHandler(AbstractRequestHandler):
    """ Handler for Account Intent. """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SafraPayAccountIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        option = slots["option"].value
        date = slots["date"].value
        
        attributes_manager = handler_input.attributes_manager
        
        attr = attributes_manager.persistent_attributes
        persisted_cpf = attr['cpf']
        
        logger.info("CPF: {}".format(persisted_cpf))
        logger.info("Option: {}".format(option))
        
        # Get any existing attributes from the incoming request
        session_attr = attributes_manager.session_attributes
        
        session_attr["date"] = date
        session_attr["option"] = option
        
        if (option == "received amount") :
            received_amount = authentication_controller('authorization/howMuchReceived',persisted_cpf,date)
            
            if (received_amount == '') :
                logger.error("Empty API response.")
                return ''
            else :
                session_attr["received_amount"] = received_amount
                speak_output = 'Here\'s your received amount on {date}: R$ {received_amount}.'.format(date=date, received_amount=received_amount)
                
                # Add speak_output variable to session attributes
                session_attr["previous_speak_output"] = speak_output
                
                # Add APL Template if device is compatible
                apl_utils.received_amount_screen(handler_input)

        elif (option == "sold amount") :
            sold_amount = authentication_controller('authorization/howMuchSell',persisted_cpf,date)
            
            if (sold_amount == '') :
                logger.error("Empty API response.")
                return ''
            else :
                session_attr["sold_amount"] = sold_amount
                speak_output = 'Here\'s your sold amount on {date}: R$ {sold_amount}.'.format(date=date, sold_amount=sold_amount)
                
                # Add speak_output variable to session attributes
                session_attr["previous_speak_output"] = speak_output
                
                # Add APL Template if device is compatible
                apl_utils.sold_amount_screen(handler_input)
        else :
            future_amount = authentication_controller('authorization/howFutureSettlementSchedule',persisted_cpf,date)
            
            if (future_amount == '') :
                logger.error("Empty API response.")
                return ''
            else :
                session_attr["future_amount"] = future_amount
                speak_output = 'Here\'s your future amount on {date}: R$ {future_amount}.'.format(date=date, future_amount=future_amount)
                
                # Add speak_output variable to session attributes
                session_attr["previous_speak_output"] = speak_output
                
                # Add APL Template if device is compatible
                apl_utils.future_amount_screen(handler_input)
         
        # Return to "menu".
        return AuthenticationIntentHandler.handle(self, handler_input)


class HelpIntentHandler(AbstractRequestHandler):
    """
    Handles AMAZON.HelpIntent requests sent by Alexa
    """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

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
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

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
        return is_request_type("SessionEndedRequest")(handler_input)

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
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = get_intent_name(handler_input)
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

class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale[:2]))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = language_data[locale[:2]]
        # if a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(HasClientInfoLaunchRequestHandler())
sb.add_request_handler(LaunchRequestIntentHandler())
sb.add_request_handler(AuthenticationIntentHandler())
sb.add_request_handler(BankingIntentHandler())
sb.add_request_handler(SafraPayIntentHandler())
sb.add_request_handler(AccountIntentHandler())
sb.add_request_handler(SafraPayAccountIntentHandler())
sb.add_request_handler(CaptureCPFIntentHandler())
sb.add_request_handler(CaptureCelphoneIntentHandler())
sb.add_request_handler(CaptureAccountIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

# register response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
