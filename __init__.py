# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.
import os

from adapt.intent import IntentBuilder
from mycroft import Message
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from tinydb import TinyDB, Query
# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.

# TODO: Change "Template" to a unique name for your skill

class HoverSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(HoverSkill, self).__init__(name="HoverSkill")
        self.db = TinyDB('db.json')
        self.empty_item = {
            "classname":"",
            "locations":[],
            "match_amount":0,
            "info":""
        }
        LOG.info("Working in...")
        LOG.info(os.path.abspath("."))

    # The "handle_xxxx_intent" function is triggered by Mycroft when the
    # skill's intent is matched.  The intent is defined by the IntentBuilder()
    # pieces, and is triggered when the user's utterance matches the pattern
    # defined by the keywords.  In this case, the match occurs when one word
    # is found from each of the files:
    #    vocab/en-us/Hello.voc
    #    vocab/en-us/World.voc
    # In this example that means it would match on utterances like:
    #   'Hello world'
    #   'Howdy you great big world'
    #   'Greetings planet earth'
    @intent_handler(IntentBuilder("HoverGetIntent").require("hover_get"))
    def handle_get_intent(self, message):
        LOG.info("Doing a get")
        LOG.info(message)
        objectname = message.data["utterance"].split()[1]
        try:
            classinfo = Query()
            res = self.db.search(classinfo.classname == objectname)
            if len(res) == 0:
                self.speak("Sorry, I don't know what that is")
                return
            item = objectname
            information = res[0]["info"]
            additional = ""
            self.speak_dialog("hover.info", data={"item": item, "information": information, "additional": additional})

            testmessage = Message("hover_get", data={
                "status": "success",
                "error": ""
            })
            self.emitter.emit(testmessage)

        except:
            self.speak("Sorry, I don't know what that is")
            testmessage = Message("hover_get", data={
                "status": "fail",
                "error": "No matches"
            })
            self.emitter.emit(testmessage)

    @intent_handler(IntentBuilder("HoverPutIntent").require("hover_put"))
    def handle_put_intent(self, message):
        LOG.info("Starting registration")

        objectname = message.data["utterance"].split()[1]
        

        #Handlers
        def yesnovalidation(utternance):
            return "yes" in utternance or "no" in utternance
        def yesnofail(utterance):
            return "Please only say yes or no"
        res = self.get_response("hover.registerconfirm",data={"object":objectname},
                                validator=yesnovalidation,on_fail=yesnofail,num_retries=1)
        if "yes" in res:
            #handleyes
            def infovalidation(utternance):
                return True

            def infofail(utterance):
                return "Please restart the registration process..."

            objectinformation = self.get_response("hover.requestinfo", data={"item": objectname})

            data = self.empty_item.copy()

            data["classname"] = objectname
            data["info"] = objectinformation

            self.db.insert(data)
            self.speak("Registration completed")
            testmessage = Message("hover_put", data={
                "status": "success",
                "error": ""
            })
            self.emitter.emit(testmessage)
        else:
            self.speak("Alright")
            testmessage = Message("hover_put", data={
                "status": "success",
                "error": "user cancelled"
            })

        LOG.info("Registration finished")


    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    def stop(self):
        self.speak_dialog("Stopping Hover skill")
        return False


# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return HoverSkill()
