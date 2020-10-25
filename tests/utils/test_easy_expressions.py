import re

import pytest

from botkit.utils.easy_expressions import Easy


class TestEasy:
    def test_easy_test(self):
        easy = Easy().start_of_line().exactly(1).of("p")
        assert easy.test("p")
        assert not easy.test("qp")

    def test_match(self):
        easy = Easy().start_of_line().exactly(1).of("p")
        assert easy.match("q") is None
        assert easy.match("p") is not None

    def test_search(self):
        easy = Easy().start_of_line().exactly(1).of("p")
        assert easy.search("q") is None
        assert easy.search("p") is not None

    def empty_assert(self, assertme):
        assert assertme != ""
        assert assertme != None

    ##
    # Example Tests
    ##

    def test_dollars_example(self):
        """
        The first example from the README.
        """

        reg = Easy().find("$").min(1).digits().then(".").digit().digit().get_regex()

        test = "$10.00"
        assert len(re.findall(reg, test)) == 1

        test = "$1X.00"
        assert not len(re.findall(reg, test)) == 1

        test = "Dollar $ign. 12. Hello. 99."
        assert not len(re.findall(reg, test)) == 1

    def test_cc_example(self):
        """
        Searches for Credit Cards
        """

        easy = (
            Easy()
            .digit()
            .digit()
            .digit()
            .digit()
            .then("-")
            .digit()
            .digit()
            .digit()
            .digit()
            .then("-")
            .digit()
            .digit()
            .digit()
            .digit()
            .then("-")
            .digit()
            .digit()
            .digit()
            .digit()
        )

        test_s = "4444-5555-6666-7777"
        assert easy.test(test_s)

        test_s = "444-555-666-777"
        assert not easy.test(test_s)

        test_s = "Hey Joe! The credit card number for the invoice is 4444-5555-6666-7777. Thanks!"
        assert easy.test(test_s)

        test_s = "Hey JoeBot4444-5555-! Your PIN number is 2222-3333."
        assert not easy.test(test_s)

    @pytest.mark.xfail
    def test_names(self):
        """
        Searches for possible names.
        """

        easy = Easy().upper_letter().lower_chats().then(" ").upper_letter().lower_chats()

        assert easy.test("The two rappers who really run the south are Paul Wall and Slim Thug.")
        assert not easy.test("Philadelphia.")

        # TODO: this fails...
        assert not easy.test("Hey lol this isnt a name. Test.")

    def test_us_phone_numbers(self):
        """
        Searches for US phone numbers.
        """

        easy = (
            Easy()
            .find("(")
            .digit()
            .digit()
            .digit()
            .then(")")
            .then(" ")
            .digit()
            .digit()
            .digit()
            .then("-")
            .digit()
            .digit()
            .digit()
            .digit()
        )
        test_s = "Hey Mike, give me a call at (123) 555-1234. Thanks!"
        assert easy.test(test_s)

        test_s = "Hey Joe! The credit card number for the invoice is 4444-5555-6666-7777. Thanks!"
        assert not easy.test(test_s)

    ##
    # Function Specific Tests
    ##

    def test_startOfLine(self):
        """
        Start of Line test.
        """

        reg = Easy().start_of_line().exactly(1).of("p").get_regex()

        test = "p"
        assert len(re.findall(reg, test)) == 1

        test = "qp"
        assert len(re.findall(reg, test)) == 0

    def test_exactly(self):
        """
        Test 'exactly'
        """
        reg = Easy().start_of_line().exactly(3).of("x").end_of_line().get_regex()

        test = "xx"
        assert len(re.findall(reg, test)) == 0
        test = "xxx"
        assert len(re.findall(reg, test)) == 1
        test = "xxxx"
        assert len(re.findall(reg, test)) == 0

    def test_max(self):
        """
        Test 'max'
        """
        reg = Easy().start_of_line().max(3).of("x").end_of_line().get_regex()

        test = "xx"
        assert len(re.findall(reg, test)) == 1
        test = "xxx"
        assert len(re.findall(reg, test)) == 1
        test = "xxxx"
        assert len(re.findall(reg, test)) == 0

    def test_min_max(self):
        """
        Test joined Min and Max
        """
        reg = Easy().start_of_line().min(3).max(5).of("x").end_of_line().get_regex()

        test = "xx"
        assert len(re.findall(reg, test)) == 0
        test = "xxx"
        assert len(re.findall(reg, test)) == 1
        test = "xxxx"
        assert len(re.findall(reg, test)) == 1
        test = "xxxxx"
        assert len(re.findall(reg, test)) == 1
        test = "xxxxxx"
        assert len(re.findall(reg, test)) == 0

    def test_of(self):
        """
        Test of
        """
        easy = Easy().start_of_line().exactly(2).of("p p p ").end_of_line()

        test = "p p p p p p "
        assert easy.test(test)
        test = "p p p p pp"
        assert not easy.test(test)

    def test_of_any(self):
        """
        Test ofAny
        """
        easy = Easy().start_of_line().exactly(3).ofAny().end_of_line()

        assert easy.test("abc")
        assert not easy.test("ac")

    def test_groups(self):
        """
        Test asGroup and ofGroup
        """
        easy = (
            Easy()
            .start_of_line()
            .exactly(3)
            .of("p")
            .as_group()
            .exactly(1)
            .of("q")
            .exactly(1)
            .of_group(1)
            .end_of_line()
        )

        assert easy.test("pppqppp")
        assert not easy.test("pxpqppp")

    def test_from(self):
        """
        Test asGroup and ofGroup
        """
        easy = (
            Easy()
            .start_of_line()
            .exactly(3)
            .of("p")
            .as_group()
            .exactly(1)
            .of("q")
            .exactly(1)
            .of_group(1)
            .end_of_line()
        )

        assert easy.test("pppqppp")
        assert not easy.test("pxpqppp")

    def test_ptbchat_example(self):
        easy = (
            Easy()
            .start_of_line()
            .exactly(1)
            .of("-")
            .whitespace()
            .anything()
            .as_group()
            .add_flag("DOTALL")
        )

        assert easy.search("- abc").group(1).strip() == "abc"
