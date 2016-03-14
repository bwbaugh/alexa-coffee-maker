"""Coffee maker is an Alexa skill that helps with coffee questions.

The primary use is to calculate the number of scoops of coffee grounds
to use given the ratio of scoops to cups that we use at home.
"""
from __future__ import division

import json
import logging


SCOOPS_PER_CUP = 5 / 6

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.info('Loading function.')


def lambda_handler(event, context):
    """Route the incoming request."""
    log.info('Received event: %s', json.dumps(event, sort_keys=True))
    func = {
        'LaunchRequest': on_launch,
        'IntentRequest': on_intent,
        'SessionEndedRequest': on_session_ended,
    }[event['request']['type']]
    response = func(request=event['request'], session=event['session'])
    log.info('Sending response: %s', json.dumps(response, sort_keys=True))
    return response


def on_launch(request, session):
    """User launched the skill without specifying what they want."""
    return get_welcome_response()


def on_intent(request, session):
    """Called when the user specifies an intent for this skill."""
    intent = request['intent']
    intent_name = request['intent']['name']
    if intent_name == "ScoopsForCupsIntent":
        return get_scoops_for_cups(intent=intent, session=session)
    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    raise ValueError('Invalid intent: {0}'.format(intent_name))


def on_session_ended(request, session):
    """Called when the user ends the session.

    Is not called when the skill returns ``should_end_session=true``.

    Useful for cleanup logic, if needed.
    """
    return None


def get_welcome_response():
    """Called when the skill is opened without an intent."""
    return build_response(
        # If we wanted to initialize the session to have some
        #   attributes we could add those here.
        session_attributes={},
        speechlet_response=build_speechlet_response(
            card_title=None,
            output="How many cups of coffee are you making?",
            reprompt_text=None,
            should_end_session=False,
        ),
    )


def get_scoops_for_cups(intent, session):
    """Calculate the number of scoops to use for some cups of water."""
    if 'Cups' in intent['slots']:
        try:
            num_cups = int(intent['slots']['Cups']['value'])
        except KeyError:
            speech_output = "I'm not sure how many cups you're making."
            should_end_session = False
        else:
            speech_output = (
                'Use {num_scoops:.2g} scoops for {num_cups} cups.'
            ).format(
                num_scoops=num_cups * SCOOPS_PER_CUP,
                num_cups=num_cups,
            )
            should_end_session = True
    else:
        speech_output = "I'm not sure how many cups you're making."
        should_end_session = False
    return build_response(
        session_attributes={},
        speechlet_response=build_speechlet_response(
            card_title='Coffee scoops',
            output=speech_output,
            # Setting reprompt_text to None signifies that we do not
            #   want to reprompt the user. If the user does not respond
            #   or says something that is not understood, the session
            #   will end.
            reprompt_text=None,
            should_end_session=should_end_session,
        ),
    )


def build_response(session_attributes, speechlet_response):
    """Helper to build the response sent back to Alexa."""
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_speechlet_response(
        card_title, output, reprompt_text, should_end_session):
    """Helper to format the speech and card data."""
    response = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output,
        },
        'card': None,
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text,
            },
        },
        'shouldEndSession': should_end_session,
    }
    if card_title:
        response['card'] = {
            'type': 'Simple',
            'title': card_title,
            'content': output,
        }
    return response
