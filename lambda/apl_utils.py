import json
import time
import prompts
import utils
from utils import get_image

import ask_sdk_core as Alexa
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode
)
from ask_sdk_core.utils import (get_supported_interfaces)

def _load_apl_document(file_path):
    """
    Load the apl json document at the path into a dict object
    """
    with open(file_path) as f:
        return json.load(f)

APL_DOCS = {
    'launchRequestIntent': _load_apl_document('./documents/launchRequestIntent.json'),
    'authenticateIntent': _load_apl_document('./documents/authenticateIntent.json'),
    'safraPay': _load_apl_document('./documents/safraPay.json'),
    'hasClientInfo': _load_apl_document('./documents/hasClientInfo.json')
}

def supports_apl(handler_input):
    """
    Checks whether APL is supported by the User's device
    """
    supported_interfaces = get_supported_interfaces(
        handler_input)
    return supported_interfaces.alexa_presentation_apl != None

def launch_request_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['launchRequestIntent'],
                datasources=generateLaunchRequestIntentScreenDatasource(handler_input)
            )
        )

def capture_cpf_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['launchRequestIntent'],
                datasources=generateCaptureCpfIntentScreenDatasource(handler_input)
            )
        )

def capture_celphone_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['launchRequestIntent'],
                datasources=generateCaptureCelphoneIntentScreenDatasource(handler_input)
            )
        )

def capture_account_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['launchRequestIntent'],
                datasources=generateCaptureAccountIntentScreenDatasource(handler_input)
            )
        )

def authentication_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['authenticateIntent'],
                datasources=generateAuthenticationIntentScreenDatasource(handler_input)
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="launchToken",
                commands=[
                    AutoPageCommand(
                        component_id="pagerComponentId",
                        duration=1000)
                ]
            )
        )

def safrapay_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['safraPay'],
                datasources=generateSafraPayIntentScreenDatasource(handler_input)
            )
        )

def has_client_info_intent_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['hasClientInfo'],
                datasources=generateHasClientInfoIntentScreenDatasource(handler_input)
            )
        )

def sold_amount_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['hasClientInfo'],
                datasources=generateSoldAmountScreenDatasource(handler_input)
            )
        )

def future_amount_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['hasClientInfo'],
                datasources=generateHasClientInfoIntentScreenDatasource(handler_input)
            )
        )

def received_amount_screen(handler_input):
    """
    Adds Launch Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="launchToken",
                document=APL_DOCS['hasClientInfo'],
                datasources=generateHasClientInfoIntentScreenDatasource(handler_input)
            )
        )

def generateLaunchRequestIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "What's your CPF number?",
                "textStyle": "textStyleDisplay3",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }

def generateCaptureCpfIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    attributes_manager = handler_input.attributes_manager
        
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    
    cpf = session_attr["cpf"]
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Your CPF is {}. What's your celphone number?".format(cpf),
                "textStyle": "textStyleDisplay4",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }

def generateCaptureCelphoneIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    attributes_manager = handler_input.attributes_manager
        
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    
    celphone = session_attr["celphone"]
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Your celphone is {}. What's your account number?".format(celphone),
                "textStyle": "textStyleDisplay4",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }

def generateCaptureAccountIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    attributes_manager = handler_input.attributes_manager
        
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    
    account_number = session_attr["account_number"]
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Your account number is {}. Please, confirm the token we sent to your celphone...".format(account_number),
                "textStyle": "textStyleDisplay5",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }

def generateAuthenticationIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    attributes_manager = handler_input.attributes_manager
        
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "* * * *<br>Token succesfully validated",
                "textStyle": "textStyleDisplay5",
                "textToDisplay2": "Which service do you want?",
                "textStyle2": "textStyleDisplay4",
                "backgroundImage": get_image('background'),
                "listItemBackground": get_image('listItemBackground')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            },
            "imageListData": {
                "type": "object",
                "listItems": [
                    {
                        "primaryText": "Safra Pay",
                        "imageAlignment": "center",
                        "imageSource": get_image('safraPay'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "safraPay",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    },
                    {
                        "primaryText": "Safra Banking",
                        "imageAlignment": "left",
                        "imageSource": get_image('safraBanking'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "safraBanking",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    },
                    {
                        "primaryText": "Morning Calls",
                        "imageAlignment": "left",
                        "imageSource": get_image('morningCalls'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "morningCalls",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    }
                ]
            }
        },
        "sources": {}
    }

def generateSafraPayIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay2": "Please choose service and date.",
                "textStyle2": "textStyleDisplay4",
                "backgroundImage": get_image('background'),
                "listItemBackground": get_image('listItemBackground')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            },
            "imageListData": {
                "type": "object",
                "listItems": [
                    {
                        "primaryText": "Sold Amount",
                        "imageAlignment": "center",
                        "imageSource": get_image('soldAmount'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "soldAmount",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    },
                    {
                        "primaryText": "Received Amount",
                        "imageAlignment": "left",
                        "imageSource": get_image('receivedAmount'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "receivedAmount",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    },
                    {
                        "primaryText": "Future Amount",
                        "imageAlignment": "left",
                        "imageSource": get_image('futureAmount'),
                        "primaryAction": [
                            {
                                "type": "SetValue",
                                "componentId": "futureAmount",
                                "property": "headerTitle",
                                "value": ""
                            }
                        ]
                    }
                ]
            }
        },
        "sources": {}
    }

def generateHasClientInfoIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    # Extract persistent attributes
    attr = handler_input.attributes_manager.persistent_attributes
    persisted_cpf = attr['cpf']
    persisted_celphone = attr['celphone']
    persisted_account_number = attr['account_number']

    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Welcome back!",
                "textStyle": "textStyleDisplay3",
                "textToDisplay2": "CPF: {}".format(persisted_cpf),
                "textStyle2": "textStyleDisplay4",
                "textToDisplay3": "Cell phone: {}".format(persisted_celphone),
                "textStyle3": "textStyleDisplay4",
                "textToDisplay4": "Account #: {}".format(persisted_account_number),
                "textStyle4": "textStyleDisplay4",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }

def generateSoldAmountScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(data[prompts.BANK_NAME])
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    date = session_attr['date']
    sold_amount = session_attr['sold_amount']
    
    # Extract persistent attributes
    attr = handler_input.attributes_manager.persistent_attributes
    persisted_cpf = attr['cpf']
    persisted_celphone = attr['celphone']
    persisted_account_number = attr['account_number']

    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Sold Amount Service",
                "textStyle": "textStyleDisplay3",
                "textToDisplay2": "Sold amount on {date}: {}".format(persisted_cpf),
                "textStyle2": "textStyleDisplay4",
                "backgroundImage": get_image('background')
            },
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }