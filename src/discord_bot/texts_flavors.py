import random

CLEAR_TODOLIST_FLAVOR = [
    "Your todo list has been cleared. Clearly, the needs of your teammates were… optional.",
    "Todo list cleared. It’s almost like your teammates didn’t need those items after all.",
    "Your todo list is now empty. Maybe your teammates will find a way to get those items themselves? Who knows.",
    "Todo list cleared. It’s almost as if your teammates were just asking for the sake of asking, without any real need for those items.",
    "Your todo list has been cleared. It’s almost like your teammates were just trying to make you feel useful, without any real intention of actually needing those items.",
    "Your todo list has been cleared. Your teammates' requests have been respectfully ignored.",
    "Your todo list has been cleared. Your teammates will surely appreciate how little you care.",
    "Your todo list has been cleared. A bold statement that other players' needs are, indeed, none of your concern.",
    "Your todo list has been cleared. Who needs to cooperate anyway?"
]

TODOLIST_FLAVOR = [
    "Here's the list of items your teammates desperately needed. Don't worry, it's not like they actually needed them or anything.",
    "Behold, the highly negotiated list of items your teammates absolutely needed. It's almost as if they were just asking for the sake of asking, without any real need for those items.",
    "Here lies the completely reasonable list of things your team expects you to grab",
    "Behold: a small and absolutely not overwhelming list of urgent necessities",
    "Here’s what your team casually decided you should handle",
    "Ah yes, the list of items that somehow became your responsibility",
    "Behold: the result of intense negotiations you were not invited to",
    "Here’s the short list of things your teammates gently insist you pick up",
    "Presenting: the entirely optional (but actually not) list of items",
    "Behold: the collective wish list your teammates have entrusted to you",
    "Here’s what your team believes is a perfectly reasonable workload",
    "Ah, the famous list of 'quick stops' your teammates mentioned",
    "Your teammates left you a little list. How nice of them",
    "Guess who’s picking these up?",
    "You’re gonna love this list",
    "This has your name all over it, apparently",
    "Not sure how, but this is on you now"
]

EMPTY_TODOLIST_FLAVOR = [
    "Congratulations! Your todo list is empty.",
    "All clear! No items on your todo list.",
    "Your todo list is currently empty. Enjoy the calm before the storm!",
    "Nothing to see here! Your todo list is empty.",
    "Your todo list is as empty as your teammates' promises to help.",
    "No tasks. Did your teammates forget about you?",
    "You have no assigned tasks. This feels wrong.",
    "No items. Did they lose faith in you?",
    "No tasks. Try not to get used to it.",
    "A rare moment of peace. Cherish it.",
    "For once, the list is empty. A miracle.",
    "You stand unburdened. For now.",
    "A truly impressive list of zero items."
]

FULFILLED_WISH_FLAVOR = [
    "{player1} dragged themselves to {location} to retrieve {item} for {player2}. Against better judgment, they complied.",
    "{player1} returned from {location} with {item} for {player2}. Yes, it was as unnecessary as it sounds.",
    "{player1} fetched {item} at {location} for {player2}. A perfect example of wasted potential.",
    "{player1} completed {player2}'s demand for {item} from {location}. Nothing says teamwork like exploitation.",
    "{player1} went to {location}, got {item}, and handed it to {player2}. Truly, a career-defining low point.",
    "{player1} obtained {item} from {location} for {player2}. Hope it was worth the existential damage.",
    "{player1} served {player2} by retrieving {item} at {location}. The hierarchy is now clear.",
    "{player1} brought back {item} from {location} for {player2}. One step closer to realizing they can be sent anywhere.",
    "{player1} fulfilled {player2}'s little wish for {item} from {location}. How quaintly one-sided.",
    "{player1} retrieved {item} at {location} for {player2}. Labor distribution remains a hilarious concept.",
    "{player1} wasted their time at {location} acquiring {item} for {player2}. Hope that felt important.",
    "{player1} obeyed and fetched {item} from {location} for {player2}. No one is surprised.",
    "{player1} completed the ritual of servitude: {item} secured at {location} for {player2}.",
    "{player1} brought {item} from {location} to {player2}. Delegation success. Self-respect failure.",
    "{player1} returned with {item} from {location} for {player2}. Congratulations on enabling this behavior.",
    "{player1} handled {item} acquisition at {location} for {player2}. They will absolutely be asked again.",
    "{player1} fetched {item} from {location} for {player2}. Efficiency was not the goal—obedience was.",
    "{player1} completed the errand for {player2}: {item} from {location}. A thrilling use of talent.",
    "{player1} secured {item} at {location} for {player2}. No reward was mentioned. Of course.",
    "{player1} did the thing again: got {item} from {location} for {player2}. Character development unclear.",
    "{player1} heroically fulfilled {player2}'s totally reasonable request by fetching {item} from {location}. Truly inspiring teamwork.",
    "{player1} went all the way to {location} to get {item} for {player2}. Because apparently, no one else could.",
    "{player1} delivered {item} from {location} to {player2}. Cooperation achieved. Barely.",
    "{player1} picked up {item} at {location} for {player2}. A sacrifice that will not be remembered.",
    "{player1} successfully retrieved {item} from {location} for {player2}. The bar was low, but still.",
    "{player1} got {item} from {location} for {player2}. Let’s all pretend this was a team effort.",
    "{player1} made the bold journey to {location} and returned with {item} for {player2}. Someone had to do it.",
    "{player1} answered {player2}'s call by grabbing {item} at {location}. Reluctantly, probably.",
    "{player1} fulfilled {player2}'s wish for {item} from {location}. A shocking display of competence.",
    "{player1} brought back {item} from {location} for {player2}. Expectations were exceeded. Slightly.",
    "{player1} handled {player2}'s request for {item} at {location}. Truly, a one-person team.",
    "{player1} secured {item} from {location} for {player2}. The rest of the team watched, surely.",
    "{player1} fetched {item} at {location} for {player2}. Because delegating is easier than helping.",
    "{player1} completed the mission: {item} acquired at {location} for {player2}. Applause is optional.",
    "{player1} went to {location}, got {item}, and gave it to {player2}. Efficiency or just resignation?",
    "{player1} made sure {player2} got their precious {item} from {location}. Priorities, clearly.",
    "{player1} retrieved {item} from {location} for {player2}. A task no one else mysteriously volunteered for.",
    "{player1} delivered {item} from {location} to {player2}. The definition of teamwork has been stretched.",
    "{player1} grabbed {item} at {location} for {player2}. Because saying no was apparently not an option.",
    "{player1} fulfilled {player2}'s request for {item} from {location}. Against all odds (and motivation)."
]

WISHLIST_FLAVORS = [
    "Here’s the list of items you’re currently hoping others will find for you. No pressure, of course.",
    "Ah yes, the things you’d rather let others deal with. Efficient.",
    "Here’s everything you’ve politely outsourced to your teammates.",
    "Behold: your personal wishlist, generously delegated to others.",
    "Here’s what you’re waiting for others to magically deliver.",
    "A curated list of problems you’ve decided are someone else’s responsibility.",
    "Here’s what you’re relying on your teammates for. Bold strategy.",
    "Ah, the list of items you confidently expect others to handle.",
    "Here’s your 'I’ll let someone else do it' collection.",
    "Behold: the items you are absolutely not going out of your way to find.",
    "Here’s what you’re hoping will just… happen.",
    "A neat summary of things you expect to receive without lifting a finger.",
    "Here’s your contribution to teamwork: expectations.",
    "Ah yes, the famous list of 'someone else will get it'.",
    "Here’s everything you’ve decided is a group problem now.",
    "Behold your requests, carefully crafted and entirely someone else’s problem.",
    "Here’s what you’re waiting on. No rush… for you, at least.",
    "A fine selection of items you’d love to receive someday.",
    "Here’s your dependency list. Good luck to everyone else.",
    "Everything you need, and none of it your responsibility. Impressive."
]

def get_clear_todolist_flavor() -> str :
    return random.choice(CLEAR_TODOLIST_FLAVOR)

def get_todolist_flavor() -> str :
    return random.choice(TODOLIST_FLAVOR)

def get_empty_todolist_flavor() -> str :
    return random.choice(EMPTY_TODOLIST_FLAVOR)

def get_fulfilled_wish_flavor(player_sending: str, player_recieving: str, item: str, location: str) -> str :
    flavor = random.choice(FULFILLED_WISH_FLAVOR)
    return flavor.format(player1=player_sending, player2=player_recieving, item=item, location=location)

def get_wishlist_flavor() -> str :
    return random.choice(WISHLIST_FLAVORS)