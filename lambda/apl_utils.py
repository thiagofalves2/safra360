import json
import recipes
import prompts
import recipe_utils
import utils
from utils import get_image

import ask_sdk_core as Alexa
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand, HighlightMode
)
from ask_sdk_core.utils import (get_supported_interfaces)

def _load_apl_document(file_path):
    """
    Load the apl json document at the path into a dict object
    """
    with open(file_path) as f:
        return json.load(f)

APL_DOCS = {
    'launchRequestIntent': _load_apl_document('./documents/launchRequestIntent.json')
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

def generateLaunchRequestIntentScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Launch Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    #print(str(data))
    
    # Define header title nad hint
    skill_name = data[prompts.SKILL_NAME]
    header_subtitle = data[prompts.HEADER_TITLE].format(prompts.BANK_NAME)
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "What's your CPF number?",
                "backgroundImage": get_image('background')
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
    header_subtitle = data[prompts.HEADER_TITLE].format(prompts.BANK_NAME)
    #hint_text = data[prompts.HINT_TEMPLATE].format(random_recipe['name'])
    
    attributes_manager = handler_input.attributes_manager
        
    # Get any existing attributes from the incoming request
    session_attr = attributes_manager.session_attributes
    
    cpf = session_attr["cpf"]
    
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "Thanks, I'll remember that your CPF is {}. What's your celphone number?".format(cpf),
                "backgroundImage": get_image('background')
            "basicHeaderData": {
                "headerTitle": skill_name,
                "headerSubtitle": header_subtitle,
                "headerAttributionImage": get_image('logo')
            }
        },
        "sources": {}
    }





def helpScreen(handler_input):
    """
    Adds Help Screen (APL Template) to Response
    """
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="helpScreen",
                document=APL_DOCS['help'],
                datasources=generateHelpScreenDatasource(handler_input)
            )
        )


def recipeScreen(handler_input, sauce_item, selected_recipe):
    """
    Adds Recipe Screen (APL Template) to Response
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    # Get prompt and reprompt speech
    reprompt_output = data[prompts.RECIPE_REPEAT_MESSAGE]
    speak_output = selected_recipe['instructions'] + " " + data[prompts.RECIPE_NOT_FOUND_REPROMPT]
    # Only add APL directive if User's device supports APL
    if(supports_apl(handler_input)):
        # Add APL Template amd Command (Speak Item to sync. Voice/Text)
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="sauce-boss",
                document=APL_DOCS['recipe'],
                datasources=generateRecipeScreenDatasource(
                    handler_input, sauce_item, selected_recipe)
            )).add_directive(
                ExecuteCommandsDirective(
                    token="sauce-boss",
                    commands=[
                        SpeakItemCommand(
                            component_id="recipeText",
                            highlight_mode=HighlightMode.line)
                    ]
                )
        )
        # As speech will be done by APL Command (SpeakItem) Voice/Text sync
        # Save prompt and reprompt for repeat
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['speak_output'] = speak_output
        session_attributes['reprompt_output'] = reprompt_output
    else:
        # As APL is not supported by device
        # Provide prompt & reprompt instead of APL Karaoke
        handler_input.response_builder.speak(speak_output).ask(reprompt_output)


def generateRecipeScreenDatasource(handler_input, sauce_item, selected_recipe):
    """
    Compute the JSON Datasource associated to APL Recipe Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    # Get a random sauce name for hint
    random_sauce = recipe_utils.get_random_recipe(handler_input)
    # Define header title and hint
    header_title = data[prompts.RECIPE_HEADER_TITLE].format(
        selected_recipe['name'])
    hint_text = data[prompts.HINT_TEMPLATE].format(random_sauce['name'])
    sauce_ssml = "<speak>{}</speak>".format(selected_recipe['instructions'])
    # Generate JSON Datasource
    return {
        "datasources": {
            "basicBackgroundData": {
                "textToDisplay": "What's your CPF number?",
                "backgroundImage": "https://s2.glbimg.com/mj2m7ttOzaHYfJqIDWN_SofobuI=/984x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_63b422c2caee4269b8b34177e8876b93/internal_photos/bs/2019/B/A/DaKpMnQrAaB2ZjODB8Vw/sede-do-banco-safra-s-o-paulo-reprodu-o-facebook.png"
            },
            "basicHeaderData": {
                "headerTitle": "Safra 360",
                "headerSubtitle": "Welcome to Safra Bank",
                "headerAttributionImage": "https://logodownload.org/wp-content/uploads/2018/09/banco-safra-logo-2.png"
            }
        },
        "sources": {}
    }





def generateHelpScreenDatasource(handler_input):
    """
    Compute the JSON Datasource associated to APL Help Screen
    """
    data = handler_input.attributes_manager.request_attributes["_"]
    # Define header and sub titles
    header_title = data[prompts.HELP_HEADER_TITLE]
    header_subtitle = data[prompts.HELP_HEADER_SUBTITLE]
    # Define sauces to be displayed
    saucesIdsToDisplay = ["BBQ", "CRA", "HON",
                          "PES", "PIZ", "TAR", "THO", "SEC"]
    locale = handler_input.request_envelope.request.locale
    # Get recipes
    all_recipes = recipe_utils.get_locale_specific_recipes(locale)
    sauces = []
    for k in all_recipes.keys():
        if(k in saucesIdsToDisplay):
            sauces.append({
                'id': k,
                'primaryText': data[prompts.HINT_TEMPLATE].format(all_recipes[k]['name'])
            })
    # Generate JSON Datasource
    return {
        'sauceBossData': {
            'headerTitle': header_title,
            'headerSubtitle': header_subtitle,
            'headerBackButton': (not handler_input.request_envelope.session.new),
            'items': sauces
        }
    }