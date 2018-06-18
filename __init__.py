# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.

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
        LOG.debug("Message")
        LOG.debug(message)
        Item = Query()
        res = self.db.search(Item.item_name == message)
        if len(res) == 0:
            item = "No item found"
            information = "no info"
            additional = "no additional info"
            self.speak_dialog("hover.info", data={"item": item, "information": information, "additional": additional})
        else:
            topres = res[0]
            self.speak_dialog("hover.info",data={"item":topres["item_name"],
                                                 "information":topres["item_info"],
                                                 "additional":topres["item_additional"][0] or "no additional info"})

    @intent_handler(IntentBuilder("HoverPutIntent").require("hover_put"))
    def handle_put_intent(self, message):
        LOG.info("Starting registration")

        objectname = message.data["utterance"].split()[1]
        
        testmessage = Message("hover_put",data={
            "fuck":"me"
        })
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
            
        else:
            self.speak("Alright")

        LOG.info("Registration finished")


    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    def stop(self):
        self.speak_dialog("ok")
        return False

    @intent_handler(IntentBuilder("HoverAddIntent").require("hover"))
    def handle_hello_world_intent(self, message):
        LOG.debug("Message")
        LOG.debug(message)

        item = "Potato"
        information = "really big"
        additional = "can be fried"
        # In this case, respond by simply speaking a canned response.
        # Mycroft will randomly speak one of the lines from the file
        #    dialogs/en-us/hello.world.dialog
        self.speak_dialog("hover.info", data={"item": item, "information": information, "additional": additional})

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return HoverSkill()
