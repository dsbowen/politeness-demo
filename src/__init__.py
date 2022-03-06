"""Main survey file.
"""
import os
import textwrap

from flask_login import current_user
from hemlock import User, Page
from hemlock.functional import compile, validate, test_response
from hemlock.questions import Check, Input, Label, Range, Select, Textarea
from hemlock import utils
from sqlalchemy_mutable.utils import partial


@User.route("/survey")
def seed():
    """Creates the main survey branch.

    Returns:
        List[Page]: List of pages shown to the user.
    """
    return [
        Page(
            Check(
                "Do you have a favoriable or unfavoriable opinion of Black Lives Matter?",
                ["Favorable", "Unfavorable"],
                variable="favorable"
            ),
            Textarea(
                "Why do you have this opinion?",
                variable="explanation"
            ),
            navigate=make_opposing_view_branch
        )
    ]


def make_opposing_view_branch(page):
    end_page = Page(Label("The End"))
    df = User.get_all_data()
    if "favorable" not in df:
        # no users have responded to the question yet
        return [end_page]

    df = df[df.favorable != page.questions[0].response].dropna()
    if len(df) == 0:
        # all users have agreed with this user's opinion so far
        return [end_page]

    counterargument = df.sample().explanation.values[0].replace("\n", "")
    return [
        Page(
            Range(
                f"""
                Another survey participant who disagrees with you wrote this:

                "{counterargument}"

                On a scale from 1 (completely unconvincing) to 5 (very convincing), how 
                convincing do you find this argument?
                """,
                input_tag={"min": 1, "max": 5},
                variable="convincing"
            )
        ),
        end_page
    ]