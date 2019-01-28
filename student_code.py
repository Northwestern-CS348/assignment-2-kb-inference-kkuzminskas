import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []


    # helper function for kb_retract
    def remove_for(self, fact_or_rule):
        """remove a fact or rule from the KB

        Args:
            fact (Fact) - Fact or rule to be retracted

        Returns:
            None
        """
        if isinstance(fact_or_rule, Fact):
            # remove fact from the KB
            self.facts.remove(fact_or_rule)
            print("fact removed")
        else:
            # remove rule from the KB
            self.rules.remove(fact_or_rule)
            print("rule removed")


        # remove fact from suppported_by fact or rule's supported_facts list
        for fr in fact_or_rule.supported_by:
            fr.supports_facts.remove(fact_or_rule)
            self.kb_assert(fr)

        # check if the supported fact is no longer supported
        for f in fact_or_rule.supports_facts:
            # remove fact from the supports_facts's supported_by list
            f.supported_by.remove(fact_or_rule)

            # if nothing is supporting it, and it isn't asserted, remove the fact
            if not f.asserted:
                if not f.supported_by:
                     self.remove_for(f)



        # check if the supported rule is no longer supported
        for r in fact_or_rule.supports_rules:
            # remove fact from the supports_rules's supported_by list
            r.supported_by.remove(fact_or_rule)

            # if nothing is supporting it, and it isn't asserted, remove the rule
            if not r.asserted:
                if not r.supported_by:
                     self.remove_for(r)

        return



    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here

        # only facts or rules can be input
        if not isinstance(fact_or_rule, Fact) and not isinstance(fact_or_rule, Rule):
            print("Error: Input was not a fact or Rule")
            return
        else:
            #asserted rules are never retracted, check to make sure
            if isinstance(fact_or_rule, Rule) and fact_or_rule.asserted:
                    print("Error: asserted rules can't be retracted.")
                    return

            if isinstance(fact_or_rule, Fact):
                # if the fact is asserted and supported, don't remove it
                if fact_or_rule.asserted and fact_or_rule.supported_by:
                    print("Fact is asserted and supported. Fact was not removed")
                    return

                # all other times, remove the fact
                else:
                    print("Fact was removed.")

                    self.remove_for(fact_or_rule)
            else:
                # remove the rule if it is not supported
                if not fact_or_rule.supported_by:
                    print("Rule is not supported. Rule is removed")
                    self.remove_for(fact_rule)








        return







class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        # get the first statement from the rule
        r_state1 = rule.lhs[0]

        # check to see if there is a match
        rule_bind = match(fact.statement, r_state1)

        # Make a list of new bound lhs statements
        lhs_bound = []

        # if there is a match:
        if rule_bind:
            print("match")
            # If there are other statements in the lhs
            for stat in rule.lhs[1:]:
                bound_statement = instantiate(stat, rule_bind)
                lhs_bound.append(bound_statement)
            # bind the rhs
            rhs_bound = instantiate(rule.rhs, rule_bind)

        else:
            return


        # create and add a new fact if lhs_bound is the length of lhs
        # create and add a new rule if lhs_bound is not empty

        # creating a new rule
        if len(lhs_bound) < (len(rule.lhs) - 1):
            print("new rule")
            #rule_str = "rule: (" + str(lhs_bound) + ") -> " + str(rhs_bound)

            #new_rule = read.parse_input(rule_str)
            new_rule = Rule([lhs_bound, rhs_bound])

            # append the fact and rule to the new fact's supported by list
            new_rule.supported_by.append(fact)
            new_rule.supported_by.append(rule)


            kb.kb_assert(new_rule)

            # append the new fact to the fact and rule's  supports_facts lists
            fact.supports_rules.append(new_rule)
            rule.supports_rules.append(new_rule)


        # create a new fact
        else:
            #fact_str = "fact: (" + str(rhs_bound) + ")"
            #new_fact = read.parse_input(fact_str)

            new_fact = Fact(rhs_bound)
            # append the fact and rule to the new fact's supported by list
            new_fact.supported_by.append(fact)
            new_fact.supported_by.append(rule)

            #print("{!r}".format(new_fact))

            kb.kb_assert(new_fact)

            # append the new fact to the fact and rule's  supports_facts lists
            fact.supports_facts.append(new_fact)
            rule.supports_facts.append(new_fact)
