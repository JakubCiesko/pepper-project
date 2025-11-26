# -*- coding: UTF-8 -*-

import logging
import random
import time

logger = logging.getLogger(__name__)


# Number-word mapping (up to 5), fallback for larger

NUMBER_WORDS = {
    "en": {
        0: "zero",
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        "many": "many",
    },
    "cs": {
        0: "nula",
        1: "jednou",
        2: "dvakrát",
        3: "třikrát",
        4: "čtyřikrát",
        5: "pětkrát",
        "many": "hodněkrát",
    },
}

PHRASES = {
    "en": {
        "SINGLE_FIRST_TIME": [
            "I see a {obj} for the first time!",
            "Looks like a new {obj} appeared.",
            "I'm noticing a {obj}. Haven't seen that before.",
            "Oh! A fresh sighting: {obj}.",
            "Is that a {obj}? Interesting!",
        ],
        "SINGLE_SECOND_TIME": [
            "Ah, a {obj} again. I remember it from earlier.",
            "That's the {obj} once more. I recognize it.",
            "Hmm… I’ve seen that {obj} before.",
            "The {obj} is back again!",
        ],
        "SINGLE_AGAIN": [
            "I see the {obj} again—this is the {count_word} time already!",
            "The mighty {obj}! This makes {count_word} sightings.",
            "Yep, there's a {obj}. Just like the previous {count_word} times.",
            "Oh wow, another appearance of the {obj}. {count_word} sightings and counting!",
        ],
        "MULTI_ALL_NEW": [
            "I see {objs}. All new sights!",
            "Look at that—{objs}! First time seeing them.",
            "Huh, interesting… {objs}. Haven’t seen any of those before.",
        ],
        "MULTI_ALL_KNOWN": [
            "I spot {objs} again.",
            "Here we go: {objs}, all familiar.",
            "I recognize all of these: {objs}.",
        ],
        "MULTI_MIX": [
            "I see {objs}. Some new, some familiar!",
            "There are {objs}. Interesting mix.",
            "Observing {objs}—a blend of known and unknown items.",
        ],
        "MULTI_DETAIL": [
            "I’ve seen the {obj} around here {count_word} already.",
            "That {obj}? Yeah, it shows up pretty often—{count_word} now.",
            "The {obj} is becoming a regular guest.",
        ],
    },
    "cs": {
        "SINGLE_FIRST_TIME": [
            "Vidím {obj} poprvé!",
            "Vypadá to, že se objevil nový objekt: {obj}.",
            "Všiml jsem si {obj}. To jsem ještě neviděl.",
            "Ó! Nový objekt na scéně: {obj}.",
            "Je to {obj}? Zajímavé!",
        ],
        "SINGLE_SECOND_TIME": [
            "Aha, zase {obj}. Pamatuju si ho z předtím.",
            "To je znovu {obj}. Poznávám ho.",
            "Hmm… ten {obj} jsem už viděl.",
            "{obj} je zpátky!",
        ],
        "SINGLE_AGAIN": [
            "Zase vidím {obj} — už {count_word}!",
            "Legendární {obj}! To už je {count_word}.",
            "Jo, zase {obj}. Stejně jako předchozí {count_word}.",
            "Wow, další výskyt objektu {obj}. Už {count_word} a přibývá!",
        ],
        "MULTI_ALL_NEW": [
            "Vidím {objs}. Všechny nové!",
            "Podívej — {objs}! Vidím je poprvé.",
            "Hmm, zajímavé… {objs}. Ani jeden jsem ještě neviděl.",
        ],
        "MULTI_ALL_KNOWN": [
            "Vidím zase {objs}.",
            "Tak jdeme na to: {objs}, všechno známé objekty.",
            "Všechny tyto poznávám: {objs}.",
        ],
        "MULTI_MIX": [
            "Vidím {objs}. Některé nové, některé známé!",
            "Jsou tu {objs}. Zajímavý mix.",
            "Pozoruji {objs} — směs známých i nových objektů.",
        ],
        "MULTI_DETAIL": [
            "{obj} už jsem tu viděl {count_word}.",
            "{obj}? Ano, objevuje se tu docela často — už {count_word}.",
            "{obj} se stává pravidelným návštěvníkem.",
        ],
    },
}


def get_number_word(language, count):
    if count < 1:
        count = 1
    lang_map = NUMBER_WORDS[language]
    if count in lang_map:
        return lang_map[count]
    return lang_map["many"]


class Conversation:
    def __init__(self, memory_length=10, language="en"):
        self.memory_length = memory_length
        self.language = language
        self.short_term_memory = {}  # {label: [timestamps]}

    def no_data_message(self):
        return (
            "I can't see anything."
            if self.language.lower().strip() == "en"
            else "Hmm, nic nevidím".encode("utf-8")
        )

    def observe(self, labels):
        now = time.time()
        newly_seen = []
        clean_labels = []

        # label cleaning enforceing utf-8
        for label in labels:
            if isinstance(label, unicode):
                clean_labels.append(label.encode("utf-8"))
            else:
                clean_labels.append(str(label))

        for label in clean_labels:
            if label not in self.short_term_memory:
                self.short_term_memory[label] = []
                newly_seen.append(label.encode("utf-8"))
            self.short_term_memory[label].append(now)

        logger.info("The robot sees %s for the first time.", str(newly_seen))

        forget_before = now - self.memory_length
        to_delete = []
        for label, timestamps in self.short_term_memory.items():
            new_ts = [t for t in timestamps if t >= forget_before]
            if new_ts:
                self.short_term_memory[label] = new_ts
            else:
                to_delete.append(label)

        logger.info("The robot is going to forget %s", str(to_delete))
        for label in to_delete:
            del self.short_term_memory[label]
        logger.debug("Memory: %s", str(self.short_term_memory))
        if newly_seen:
            return self.get_sentence(newly_seen)
        else:
            return self.get_sentence(
                list(set([label.encode("utf-8") for label in labels]))
            )

    def get_sentence(self, unique_labels):
        lang = self.language
        phrases = PHRASES.get(lang, PHRASES["en"])
        if len(unique_labels) == 1:
            obj = unique_labels[0]
            seen_count = len(self.short_term_memory.get(obj, []))

            # First time in memory time
            if seen_count == 1:
                patterns = phrases["SINGLE_FIRST_TIME"]
                return random.choice(patterns).format(
                    obj=obj,
                    count_word=get_number_word(self.language, seen_count),
                )

            # 2times
            elif seen_count == 2:
                patterns = phrases["SINGLE_SECOND_TIME"]
                return random.choice(patterns).format(
                    obj=obj,
                    count_word=get_number_word(self.language, seen_count),
                )
            # 3.time
            else:
                patterns = phrases["SINGLE_AGAIN"]
                return random.choice(patterns).format(
                    obj=obj,
                    count_word=get_number_word(self.language, seen_count),
                )
        join_word = " a " if lang == "cs" else " and "

        if len(unique_labels) == 2:
            joined = join_word.join(unique_labels)
        else:
            joined = ", ".join(unique_labels[:-1]) + join_word + unique_labels[-1]

        new_objs = []
        known_objs = []
        for obj in unique_labels:
            if len(self.short_term_memory.get(obj, [])) == 1:
                new_objs.append(obj)
            else:
                known_objs.append(obj)
        if len(new_objs) == len(unique_labels):
            patterns = PHRASES[lang]["MULTI_ALL_NEW"]
            return random.choice(patterns).format(objs=joined)

        if len(known_objs) == len(unique_labels):
            patterns = PHRASES[lang]["MULTI_ALL_KNOWN"]
            return random.choice(patterns).format(objs=joined)
        # some new some old
        patterns = PHRASES[lang]["MULTI_MIX"]
        return random.choice(patterns).format(objs=joined)
