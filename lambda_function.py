"""
 POC Project

"""

from __future__ import print_function

#-------------------------------------------------------------------------------#
# --------------- Event handlers ------------------
#-------------------------------------------------------------------------------#


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event, event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(event, intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    dialog_state = event['request']['dialogState']
    
    print('dialogState/n')
    print(dialog_state)

    # Dispatch to your skill's intent handlers
    if intent_name == "MortageNews":
        return whatIsNewIntent(intent, session)
    elif intent_name == "Rates":
        return getRates(intent, session)
    elif intent_name == "LoanStatus":
        return getLoanStatus(intent, session)
    elif intent_name == "LoanNextStep":
        return getLoanNextStep(intent, session)
    elif intent_name == "CallLoanOfficer":
        return askLoanOfficerIntent(intent, session)
    elif intent_name == "PaymentDueDate":
        return getPaymentDueDate(intent, session)        
    elif intent_name == "Finish":
        return closeDialog(intent, session)
    elif intent_name == "FAQLoanPreQualification":
        return FAQLoanPreQualification(intent, session)                
    elif intent_name == "FAQTypesofLoan":
        return FAQTypesofLoan(intent, session)                
    elif intent_name == "FAQApplyLoan":
        return FAQApplyLoan(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

#-------------------------------------------------------------------------------#
# --------------- Functions that control the skill's behavior ------------------
#-------------------------------------------------------------------------------#


#------------- generic ---------------------------------------------------------#

last_shopping_list = ['3M Disposable Mixing Wells 96/Pk','Absorbent Points Coarse','Acclean Floss','Aleve Caplets','Aleve Tablets']

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Beth. \nHow can I help you?"
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you need"
    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/alexa_bg_lg_v2.jpg"))

#------------- finish dialog ---------------------------------------------------------#

def closeDialog(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Ok, You are welcome!"

    # session_attributes = session['attributes']

    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, ""))
        
#------------- office ---------------------------------------------------------#

def set_office_in_session(intent, session):
    """ Sets the product in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Office' in intent['slots']:
        favorite_office = intent['slots']['Office']['value']
        session_attributes = create_favorite_office_attributes(favorite_office)
        speech_output = "I now know your office is " + \
                        favorite_office + \
                        ". You can start ordering product by saying, " \
                        "I want product and say the name of the product"
        reprompt_text = "You can start ordering product by saying, " \
                        "I want to order glove ?"
    else:
        speech_output = "I'm not sure what your office is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your office is. " \
                        "You can tell me your office by saying, " \
                        "my office is Farmingdale Center."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/alexa_bg_lg_v2.jpg"))

def create_favorite_office_attributes(favorite_office):
    return {"currentOffice": favorite_office}

#------------- cart ---------------------------------------------------------#

def get_products_in_cart(intent, session):
    session_attributes = {}
    reprompt_text = None

    if "cart_product_list" in session.get('attributes', {}):
        requested_product = session['attributes']['cart_product_list']
        #current_office = session['attributes']['currentOffice']
        session_attributes = session['attributes']

        speech_output = "Your shopping cart contains :" + requested_product + \
                        ". Would you like to check out?"
        should_end_session = False
    else:
        speech_output = "There are no products in your shopping cart, " \
                        "You can start ordering product by saying, for example, " \
                        "I want to order glove"

        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, ""))

def set_product_in_cart(intent, session):
    """ Sets the product in the session and prepares the speech to reply to the
    user.
    """

    session_attributes = {}
    card_title = intent['name']
    should_end_session = False
    reprompt_text = None

    # check valid office
    if 'currentOffice' in session.get('attributes', {}):
        current_office = session['attributes']['currentOffice']

        if 'Product' in intent['slots']:
            requested_product = intent['slots']['Product']['value']
            session_attributes = create_requested_product_attributes(current_office, requested_product, session)

            speech_output = "The requested product " + \
                            requested_product + \
                            " has been added to the shopping cart."
            reprompt_text = "You can now order more products, " \
                            "Do you want to proceed?"
        else:
            speech_output = "I'm not sure what your product is. " \
                            "Please try again."
            reprompt_text = "I'm not sure what your product is. " \
                            "You can tell me your product by saying, " \
                            "I want to order glove."
    else:
        speech_output = "Before you order, please tell me your office."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, ""))

def checkout(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "checkout executed with success, thanks"

    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, ""))

def create_requested_product_attributes(current_office, requested_product, session):
    if "cart_product_list" in session.get('attributes', {}):
        cart_product_list = session['attributes']['cart_product_list'] + "," + requested_product
    else:
        cart_product_list = requested_product

    return {"cart_product_list": cart_product_list,
            "currentOffice": current_office
            }

#------------- shopping list ---------------------------------------------------------#

def get_last_shopping_list(intent, session):

    session_attributes = {}
    reprompt_text = None

    str1 = ','.join(last_shopping_list)

    speech_output = "Your last shopping list contains : " + str1

    session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, ""))

#------------- FAQ ---------------------------------------------------------#

def FAQLoanPreQualification(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "To get started on the Mortgage Pre-Qualification process we'll contact you back within 24 hours.\n\n" \
                    "Our Mortgage Representatives will be happy to answer all your questions about the home buying process."

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))


def FAQTypesofLoan(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "We offer several different types of consumer, mortgage and personal loans that include:\n\n" \
                    "Consumer:\n" \
                    "-Home Equity\n" \
                    "-Auto (New, Used, Refinance)\n" \
                    "-Personal\n" \
                    "-Credit Card\n\n" \
                    "Mortgage Loan:\n" \
                    "-Fixed Rate Mortgagen\n" \
                    "-Adjustable Rate Mortgage\n" \
                    "-Jumbo Mortgages\n" \
                    "-FHA Mortgage\n" \
                    "-Refinance\n\n" \
                    "Business Loan:\n" \
                    "-Business Lines of Credit\n" \
                    "-Commercial Mortgages\n" \
                    "-Term Loans\n" \
                    "-Business Credit Cards"
    

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))


def FAQApplyLoan(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "You can apply online using our website\n\nwww.POCfcu.com"

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))


#------------- call loan officer ---------------------------------------------------------#

def askLoanOfficerIntent(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Ok, I got it. \n\nI will ask to your loan officer call you as soon as possible."

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))

#------------- order ---------------------------------------------------------#

def whereIsMyOrderIntent(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Your open order is ???"

    session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad2.jpg"))

def emailOrderIntent(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Ok, your order has been emailed to you"

    session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad3.jpg"))


#------------- news ---------------------------------------------------------#

def whatIsNewIntent(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Nationwide Mortgage Bankers launches platform for Spanish speakers. Nationwide Mortgage Bankers, an independent mortgage lender, has launched a mortgage platform designed for Spanish-speaking homebuyers."

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad4.jpg"))

#------------- payment due date ---------------------------------------------------------#

def getPaymentDueDate(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "Your payment due date is \n09/25"

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))

#------------- rates ---------------------------------------------------------#

def getRates(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "See Today's Fixed Mortgage Rates: \n\n30 Year Fixed, 3.375%, \n\n20 Year Fixed, 3.250%"

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session,"https://alexa-poc-bp.s3.amazonaws.com/ad2.jpg"))

#------------- loan status ---------------------------------------------------------#

def getLoanStatus(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "We've received your application. \n\nKeep in mind processing times may vary. \n\nWe estimate you should finish the process in 2-3 weeks."

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session,"https://alexa-poc-bp.s3.amazonaws.com/ad4.jpg"))


#------------- loan status ---------------------------------------------------------#

def getLoanNextStep(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "We received your documents and just finished your house evaluation! \n\nEverythinhg looks good, \n\nWe just need you to open an online account to finish up."

    # session_attributes = session['attributes']

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, "https://alexa-poc-bp.s3.amazonaws.com/ad1.jpg"))

#------------- on sale   ---------------------------------------------------------#

def whatIsOnSaleIntent(intent, session):

    session_attributes = {}
    reprompt_text = None

    speech_output = "See our hot deals! save 15% buying Led illumminated mirror, save 20% buynning 3M espe"

    session_attributes = session['attributes']
    
    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, ""))



#-------------------------------------------------------------------------------#
# --------------- Helpers that build all of the responses ----------------------
#-------------------------------------------------------------------------------#

def build_speechlet_response(title, output, reprompt_text, should_end_session, image):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': 'POC',
            'text': output,
            "image": {
                "smallImageUrl": image,
                "largeImageUrl": image
            }
        },
        'reprompt': {
            'outputSpeech': {
               'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }