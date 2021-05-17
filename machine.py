import search
import random, re
from pattern.en import DEFINITE, tag, tokenize, conjugate, singularize, referenced, wordnet
from pprint import pprint

class Invention(object):
    def __init__(self, text):
        self.source_text = text
        self.title = self.create_gerund_title(text)
        self.create_first_line()
        self.create_abstract()
        self.create_illustrations()
        self.create_description()
        self.create_claims()

    def prefix(self):
        prefixes = ["system", "method", "apparatus", "device"]
        self.prefixes = random.sample(prefixes, 2)
        title = self.prefixes[0] + " and " + self.prefixes[1] + " for "
        if random.random() < .2:
            title = "web-based " + title
        return referenced(title)


    def create_gerund_title(self, text):
        search_patterns = [
                'VBG DT NN RB', 'VBG NNP * NP', 'VBG NNP * .',
                'RB VBG NNP', 'VBG JJ NP', 'VBG * JJ * NP', 'VBG * JJ *',
                'VBG * NN', 'VBG * JJ *? NP NP?', 'VBG * JJ? NP']

        gerund_phrases = search.search_out(text, search_patterns[-1])
        self.possible_titles = []
        for title in gerund_phrases:
            self.possible_titles.append(title)
        self.partial_title = random.choice(self.possible_titles)
        title = self.prefix() + self.partial_title
        self.set_keywords(self.partial_title)
        return title.capitalize()

    def set_keywords(self, title):
        words = tag(title)
        self.nouns = [word[0] for word in words if word[1] == 'NN']
        self.verbs = [word[0] for word in words if word[1] in ['VB', 'VBZ']]
        self.adjectives = [word[0] for word in words if word[1] == 'JJ']

    def create_first_line(self):
        templates = ['{0} is provided.', '{0} is disclosed.', 'The present invention relates to {0}.']
        self.first_line = random.choice(templates).format(self.title).capitalize()

    def find_lines(self):
        lines = search.search_out(self.source_text, '|'.join(self.nouns + self.verbs + self.adjectives))
        print lines

    def key_sentences(self):
        words = set(search.hypernym_search(self.source_text, 'instrumentality'))
        sents = tokenize(self.source_text)
        pat = re.compile(' ' + '|'.join(words) + ' ')
        sents = [s for s in sents if pat.search(s) != None]

        pprint(sents)
        pprint(words)


    def sentence_walk(self):
        output = []
        sents = tokenize(self.source_text)
        words = set(search.hypernym_search(self.source_text, 'artifact'))
        pat = re.compile(' ' + '|'.join(words) + ' ')
        sents = [s for s in sents if pat.search(s) != None]
        pprint(sents)

    def create_illustrations(self):
        self.illustrations = []
        templates = ["Figure {0} illustrates {1}.",
            "Figure {0} is a schematic drawing of {1}.",
            "Figure {0} is a perspective view of {1}.",
            "Figure {0} is an isometric view of {1}.",
            "Figure {0} schematically illustrates {1}.",
            "Figure {0} is a block diagram of {1}.",
            "Figure {0} is a cross section of {1}.",
            "Figure {0} is a diagrammatical view of {1}."]
        illustrations = list(set(search.search_out(self.source_text, 'DT JJ NP IN * NN')))
        self.unformatted_illustrations = illustrations
        for i in range(len(illustrations)):
            self.illustrations.append(random.choice(templates).format(i+1, illustrations[i]))

    def create_abstract(self):
        artifacts = search.hypernym_combo(self.source_text, 'artifact', "JJ NN|NNS")
        #artifacts +=search.hypernym_combo(self.source_text, 'material', "JJ NN|NNS")
        artifacts = set(artifacts)
        self.artifacts = artifacts
        words = []
        words = [referenced(w) for w in artifacts]
        self.abstract = self.title + ". "
        self.abstract += "The devices comprises "
        self.abstract += ", ".join(words) 

    def define_word(self, word):
        synsets = wordnet.synsets(word)
        if len(synsets) > 0:
            gloss = synsets[0].gloss
            if gloss.find(';') > -1:
                gloss = gloss[:gloss.find(';')]
            word = word + " (comprising of " + gloss + ") "
        return word

    def create_description(self):
        pat = 'VB|VBD|VBZ|VBG * NN IN * NN'
        #pat = 'PRP * VB|VBD|VBZ|VBG * NN'
        phrases = search.search_out(self.source_text, pat)
        conjugated_phrases = []
        for phrase in phrases:
            words = []
            for word, pos in tag(phrase):
                if pos in ["VBZ", "VBD", "VB", "VBG"]:
                    words.append(conjugate(word, "3sg"))
                #elif pos == "NN" and random.random() < .1:
                    #words.append(self.define_word(word))
                else:
                    words.append(word)
            conjugated_phrases.append(' '.join(words))

        artifacts = list(self.artifacts)

        sentence_prefixes = ["The present invention", "The device", "The invention"]
        paragraph_prefixes = ["The present invention", "According to a beneficial embodiment, the invention", "According to another embodiment, the device", "According to a preferred embodiment, the invention", "In accordance with an alternative specific embodiment, the present invention"] 
        i = 0
        self.description = ''
        for phrase in conjugated_phrases:
            line = ""
            if i == 0:
                line = paragraph_prefixes[0] + " " + phrase
            else:
                if random.random() < .1:
                    line = "\n\n" + random.choice(paragraph_prefixes) + " " + phrase
                else:
                    line = random.choice(sentence_prefixes) + " " + phrase
            self.description += line + ". "
            i += 1

    def create_claims(self):
        independent = '{0}. {1} for {2}, comprising:'
        dependent = '{0}. {1} of claim {2}, wherein said {3} comprises {4}.'

        self.claims = []
        claim_number = 0
        for prefix in self.prefixes:
            claim_number += 1
            claim = independent.format(
                claim_number, referenced(prefix).capitalize(), self.partial_title)
            terms = random.sample(list(self.artifacts),
                                  random.randint(2, min(len(self.artifacts), 5)))
            for term in terms[:-1]:
                claim += '\n\t' + referenced(term) + '; '
            claim += 'and \n\t' + referenced(terms[-1]) + '.'
            self.claims.append(claim)
            independent_claim_number = claim_number

            for term in terms:
                claim_number += 1
                claim = dependent.format(
                    claim_number,
                    referenced(prefix, article=DEFINITE).capitalize(),
                    independent_claim_number, term,
                    random.choice(self.unformatted_illustrations))
                self.claims.append(claim)

    def body_old(self):
        output = []
        useful_phrases = search.hypernym_combo(text, 'instrumentality', 'JJ? NP')
        random.shuffle(useful_phrases)
        random.shuffle(self.possible_titles)
        for i in range(len(self.possible_titles)):
            if (i < len(useful_phrases) and self.possible_titles[i] != self.partial_title):
                output.append(useful_phrases[i] + ' for ' + self.possible_titles[i])
        return output


    def format(self):
        print self.title
        print "\n\nABSTRACT\n\n"
        print self.abstract
        print '\n\nBRIEF DESCRIPTION OF THE DRAWINGS\n\n'
        for illustration in self.illustrations:
            print illustration
            print

        print "\n\nDETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS"
        #print "\n\nThe detailed description set forth below in connection with the appended drawings is intended as a description of presently-preferred embodiments of the invention and is not intended to represent the only forms in which the present invention may be constructed or utilized. The description sets forth the functions and the sequence of steps for using the invention in connection with the illustrated embodiments. However, it is to be understood that the same or equivalent functions and sequences may be accomplished by different embodiments that are also intended to be encompassed within the spirit and scope of the invention."
        print "\n"

        print self.description

        print "\n\nWhat is claimed is:"
        for claim in self.claims:
            print "\n%s" % claim


    def make_name_one(self):
        title_combos = search.hypernym_combo(text, 'instrumentality', 'JJ NP')
        title_combos = [t for t in title_combos if t.endswith('round') == False]
        title = random.choice(title_combos)
        return title

    def specific_title(self, title):
        words = title.split()
        for i in range(len(words)):
            word = words[i]
            new_word = search.random_hyponym(word)
            if len(new_word) > 0:
                words[i] = new_word
        return ' '.join(words)


if __name__ == '__main__':

    import sys

    #text = sys.stdin.read().decode('ascii', errors='replace')
    text="""
        A. INVENTION TITLE: SmartWheel Wheelchair (Live It On wheels).
        B. PROBLEM: What overall problem(s) does the proposed invention solve or what purpose does it serve? (Note: Please be specific, spell out acronyms and provide enough layman level detail to fully explain the problem.)
        Ans: As the recent survey done by World Health Organization (WHO), over 1 billion people are estimated to live with some form of disability. This corresponds to about 15% of world population, with 190 million people age from 15 years and above and this number keep on rising with increasing population and there is no such device which can ensure their safety when they go out.
        For people who have difficulty in walking or moving around, a wheelchair is an essential requirement for mobility, empowerment, dignity, and overall well-being. Mobility can enable a wheelchair user to be independent, to participate and to have equal opportunities, to access education, employment, health care, and take part in family and community life.
        Each wheelchair user today faces problems while alone like when they face some mechanical problem in their wheel or they lose somewhere or they trip from their wheelchair or they find themselves in a falling victim situation they feel helpless and need someone to assure their security and safety. NGO(s) and other govt. Organizations/health centers/Hospitals do not have so many people to look after each and every individual facing mobility impairment.
        Even after advancement in a wheelchair, a disabled person can drive a car but still not be able to send their location to their concerned ones when they face any mishappening.
        C. EXISTING SOLUTIONS / PRIOR ART/RELATED APPLICATIONS & PATENTS:
        1. List any known products, or combination of products, currently available to solve the same problem(s). What is the present commercial practice?
        There are no such attachments present in the market commercially which comes with both panic button and location sharing functionality and is attachable to every kind of wheelchair. Only some mobile applications are available which are not handy/convenient to use in case of emergency.
        2. In what way(s) do the presently available solutions fall short of fully solving the problem?
          Presently available wheelchairs or wheelchair attachment comes with only the panic button.
        Section B: Your Invention
        - 2 -
          There are only a few wheelchairs which come with a GPS module but in those
        wheelchairs you don’t have liberty to select persons with which you want to share
        location.
          There is no such wheelchair attachment available which comes with both location sharing
        and panic button only a few wheelchairs come with it.
          These wheelchair attachments (With panic button) are only manufactured for specific
        types of wheelchair not for every kind of wheelchair.
        3. Conduct keyword searches using Google and list relevant prior art material found?
          Smart wheelchair
          Location sharing wheelchair
          Wheelchair panic button
          Safety device for disabled
          Wheelchair attachment
          Wheelchair with GPS
          Wheelchair with SOS button
        D. DESCRIPTION OF PROPOSED INVENTION:
        How does your idea solve the problem defined above? Please include details about how your
        idea is implemented and how it works?
        Ans: It is a compact device that can be attached to any kind of wheelchair.The main purpose of
        this device is to ensure safety and security of the user.
        It has 2 push buttons on it one is for sending the location to your concerned ones in case of an
        emergency and the other one is a panic button in case a user needs help from nearby and this
        entire operation is synchronised with an mobile application in order to share location.
        The person on the wheelchair can’t help him/herself from any falling victim situation in case of
        emergency therefore they need to send location to their concern ones this also allows a person
        to go alone without anyone looking after them.This also helpful for the NGOs to track any of
        their person’s location anytime to ensure their(user’s) security.
        As we all know that a person on wheelchair can be an easy target for thieves or robbers and
        this limits them to move out alone but this problem can be resolved if a panic button is there in
        which they can share their live location in case of emergency and ask for help from nearby in
        case of any victim situation.
        This device is very efficient as it consumes a very little amount of energy that is provided by a
        small battery of 400mah (can be increased) which can last weeks in a single charge.
        For sharing location we are using GPS module for first place and modern google maps api
        which fetches the wifi or cellular network nearby to track anyone's location which can be used
        Section B: Your Invention
        - 3 -
        when a proper internet connection is not available to the user or if the gps module is not working properly.
        Special variants are also provided for those who can’t press a button and their wheelchair is voice or eye controlled.In this variant instead of using push buttons we will use voice commands such as “share location” or “need help” and for eye control some special eye gestures.
        As we all know that a person on a wheelchair suffers a lot at places of high security such as Airports .There(Airports) they have a different security protocols where they have to use wheelchair provided by the authorities and sometime there wheelchair get misplaced.To avoid this situation they(user) can track the location of their wheelchair with the provided application.
        E. NOVELTY: Please provide a one-sentence description of what distinguishes your idea from the prior art. This is a statement of what is new, and not a business case.
        Ans: Our proposed model of wheelchair attachment ensures the safety of the person sitting on it in all ways because it provides the panic button as well as location sharing features and makes them independent to go out and explore the world.
        F. COMPARISON: Please provide advantages and basic differences of the proposed solution over previous solutions.
        Ans: Our product comes with location tracking and panic button features which are synchronised by an mobile application which gives an interface to our device which makes it easy to use.
        Other devices present in the market right now is just a panic button which not specifically manufactured for wheelchairs and also don’t provide user friendly service which can be used by everyone.There are some wheelchair present in the market which come with a location sharing functionality but budget is a constraint in these wheelchairs these are so expensive that only some few and privileged persons can afford those wheelchair.
        There many types of disability that an individual faces today these not just includes mobility impairment(don't be able to walk) but also vision disability and also problem in hand movements.
        So advanced variants of our product which is more expensive than base variant but still affordable to everyone comes with eye gesture and hand gesture functionality which is useful for persons suffering from both motor and vision disability.
        G. ADDITIONAL INFORMATION: Please provide additional information such as, a claim set, drawings, a software code, etc.)
        Section B: Your Invention
        - 4 -
        Our device comes in use whenever a person on a wheelchair feels uncomfortable or unsafe and need someone’s assistance or help in any victim situation or a any medical emergency he/she can press the panic button which blows a loud siren so that a nearby can help them and the location of the wheelchair will send to the person he/she has added on the mobile application.
        If the person sitting on the wheelchair falls somehow then their (person on the wheel) location will be send to their concern ones through the application.
        Section B: Your Invention
        - 5 -
        """
    invention = Invention(text)
    #for t in invention.possible_titles:
        #print invention.prefix() + t
    invention.format()
