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




    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        print("Retracting {!r}".format(fact_or_rule))
        ####################################################
        # Student code goes here

        # only facts or rules can be input
        if not isinstance(fact_or_rule, Fact) and not isinstance(fact_or_rule, Rule):
            print("Error: Input was not a fact or Rule")
            return
        else:
            #asserted rules are never retracted, check to make sure
            if isinstance(fact_or_rule, Rule):
                if fact_or_rule.asserted:
                    print("Error: asserted rules can't be retracted.")
                    return
                else:
                    for r in self.rules:
                        if r == fact_or_rule:
                            rule = r
                    # remove the rule if it is not supported
                    if not rule.supported_by:
                        print("Rule is not supported. Rule is removed")
                        # remove the rule from the supports_rules list of the facts/rules that support this fact
                        for fr in rule.supported_by:
                            if rule in fr:
                                fr[0].supports_rules.remove(rule)
                                fr[1].supporst_rules.remove(rule)

                        # check facts supported by the rule that is being removed
                        for sup_f in rule.supports_facts:
                            #remove the [fact, rule] combo that was supported by the retracted fact
                            for fr in sup_f.supported_by:
                                # fr is a [fact, rule]
                                if rule in fr:
                                    sup_f.supported_by.remove(fr)

                            # if the fact is unsupported and not asserted, remove the fact
                            if not sup_f.supported_by and not sup_f.asserted:
                                # self.kb_retract(sup_f)
                                self.facts.remove(sup_f)

                        # check the rules supported by the rule being removed
                        for sup_r in rule.supports_rules:
                            #remove the [fact, rule] combo that was supported by the retracted fact
                            for fr in sup_r.supported_by:
                                # fr is a [fact, rule]
                                if rule in fr:
                                    sup_r.supported_by.remove(fr)

                            if not sup_r.supported_by and not sup_r.asserted:
                                # self.kb_retract(sup_r)
                                self.rules.remove(sup_r)


                        # remove the retracted fact from the KB
                        self.facts.remove(fact)




            if isinstance(fact_or_rule, Fact):
                # get the fact from the KB so it has the supported_by statements
                for f in self.facts:
                    if f == fact_or_rule:
                        fact = f


                # if the fact is asserted and supported, don't remove it
                if fact.asserted and fact.supported_by:
                    print("Fact is asserted and supported. Fact was not removed")
                    return

                # all other times, remove the fact
                else:
                    print("Fact was removed.")

                    if not fact.supported_by:
                        # remove the fact from the supporst_facts list of the facts/rules that support this fact
                        for fr in fact.supported_by:
                            if fact in fr:
                                fr[0].supports_facts.remove(fact)
                                fr[1].supporst_facts.remove(fact)

                        # check facts supported by the fact that is being removed
                        for sup_f in fact.supports_facts:
                            #remove the [fact, rule] combo that was supported by the retracted fact
                            for fr in sup_f.supported_by:
                                # fr is a [fact, rule]
                                if fact in fr:
                                    sup_f.supported_by.remove(fr)

                            # if the fact is unsupported and not asserted, remove the fact
                            if not sup_f.supported_by and not sup_f.asserted:
                                # self.kb_retract(sup_f)
                                self.facts.remove(sup_f)

                        # check the rules supported by the fact being removed
                        for sup_r in fact.supports_rules:
                            #remove the [fact, rule] combo that was supported by the retracted fact
                            for fr in sup_r.supported_by:
                                # fr is a [fact, rule]
                                if fact in fr:
                                    sup_r.supported_by.remove(fr)

                            if not sup_r.supported_by and not sup_r.asserted:
                                # self.kb_retract(sup_r)
                                self.rules.remove(sup_r)


                        # remove the retracted fact from the KB
                        self.facts.remove(fact)



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
        if not lhs_bound:
            print("New fact")

            # create a new fact
            new_fact = Fact(rhs_bound, [[fact, rule]])

            # append the new fact to the fact and rule's  supports_facts lists
            fact.supports_facts.append(new_fact)
            rule.supports_facts.append(new_fact)

            kb.kb_assert(new_fact)


        # create a new rule
        else:
            print("new rule")

            # creating a new rule
            new_rule = Rule([lhs_bound, rhs_bound], [[fact, rule]])

            # append the new fact to the fact and rule's  supports_facts lists
            fact.supports_rules.append(new_rule)
            rule.supports_rules.append(new_rule)

            kb.kb_assert(new_rule)

        return
