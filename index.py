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
        card_title=None,
        output="How many cups of coffee are you making?",
        reprompt_text=None,
        should_end_session=False,
    )


def get_scoops_for_cups(intent, session):
    """Calculate the number of scoops to use for some cups of water."""
    def bad_response():
        return build_response(
            session_attributes={},
            card_title=None,
            output="I'm not sure how many cups you're making.",
            reprompt_text="How many cups of coffee are you making?",
            should_end_session=False,
        )

    try:
        num_cups = int(intent['slots']['Cups']['value'])
    except KeyError:
        return bad_response()
    return build_response(
        session_attributes={},
        card_title='Coffee scoops',
        output=(
            'Use {num_scoops:.2g} scoops for {num_cups} cups.'
        ).format(
            num_scoops=num_cups * SCOOPS_PER_CUP,
            num_cups=num_cups,
        ),
        # Setting reprompt_text to None signifies that we do not want
        #   to reprompt the user. If the user does not respond or says
        #   something that is not understood, the session will end.
        reprompt_text=None,
        should_end_session=True,
    )


def build_response(
        session_attributes, card_title, output, reprompt_text,
        should_end_session):
    """Helper to build the response sent back to Alexa."""
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': {
            'card': build_card(title=card_title, content=output),
            'outputSpeech': build_output_speech(text=output),
            'reprompt': build_reprompt(text=reprompt_text),
            'shouldEndSession': should_end_session,
        },
    }


def build_card(title, content):
    """The object containing a card to render to the Amazon Alexa App."""
    if not title:
        # XXX: Using this as a hacky way of indicating we don't want a
        #   card at all. This is hacky because it's valid to create a
        #   card without a title.
        return None
    return {
        'type': 'Simple',
        'title': title,
        'content': content,
    }


def build_output_speech(text):
    """Used for setting both the outputSpeech and the reprompt properties."""
    return {
        'type': 'PlainText',
        'text': text,
    }


def build_reprompt(text):
    """The object to use if a re-prompt is necessary.

    This is used if the your service keeps the session open after
    sending the response, but the user does not respond with anything
    that maps to an intent defined in your voice interface while the
    audio stream is open.

    If this is not set, the user is not re-prompted.
    """
    if not text:
        return None
    return {
        'outputSpeech': build_output_speech(text=text),
    }
