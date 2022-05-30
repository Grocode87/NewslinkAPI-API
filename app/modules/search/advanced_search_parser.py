from distutils.command.build import build
import json
from sqlalchemy import not_, or_, and_, text
from ...models import Article, Cluster, ClusterArticle
from ...exceptions import BadRequestException


def build_parse_tree(expression):
    """
    Given an expression ex. ((a & b) | (c & d))

    Build and return a parse tree that represents this expression

                OR
        /               \
        AND            AND
    /       \       /       \
    a       b       c       d

    """

    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    OPERATORS = "&|~"

    tree = {}
    stack = [tree]
    node = tree

    word = ""
    for token in expression:
        if (not word == "") and (
            (not token == LEFT_PAREN)
            and (not token == RIGHT_PAREN)
            and (not token in OPERATORS)
        ):
            word += token
        else:
            if not word == "":
                node["val"] = word.strip()
                word = ""
                parent = stack.pop()
                node = parent

            if token == LEFT_PAREN:
                node["left"] = {}
                stack.append(node)
                node = node["left"]

            elif token == RIGHT_PAREN:
                node = stack.pop()

            elif token in OPERATORS:
                if "right" in node:
                    print(node["right"])
                    node["right"] = {"val": token, "left": node["right"], "right": {}}
                    stack.append(node["right"])
                    node = node["right"]["right"]
                else:
                    node["val"] = token
                    node["right"] = {}
                    stack.append(node)
                    node = node["right"]

            else:
                if token != " ":
                    node["val"] = token
                    word += token
    return tree


def build_str_query(parse_tree):
    """
    Test function that traverses the parse tree and creates a string query based on that
    """

    if "left" in parse_tree and "right" in parse_tree:
        return_val = "(" + build_str_query(parse_tree["left"])
        return_val += " " + parse_tree["val"] + " "
        return_val += build_str_query(parse_tree["right"]) + ")"

        return return_val
    elif not "val" in parse_tree and "left" in parse_tree:
        return build_str_query(parse_tree["left"])
    else:
        return parse_tree["val"]


def build_query(parse_tree, filter_param):
    """
    Given a parse tree, build an sqlalchemy nested query using or_ and and_ functions
    """
    OPERATORS = {"&": and_, "|": or_, "~": not_}

    if "left" in parse_tree and "right" in parse_tree:
        operator = OPERATORS[parse_tree["val"]]
        return_val = operator(
            build_query(parse_tree["left"], filter_param),
            build_query(parse_tree["right"], filter_param),
        )

        return return_val
    elif not "val" in parse_tree and "left" in parse_tree:
        return build_query(parse_tree["left"], filter_param)

    elif not "left" in parse_tree and "right" in parse_tree:
        operator = OPERATORS[parse_tree["val"]]
        return operator(build_query(parse_tree["right"], filter_param))
    else:
        return filter_param("%" + parse_tree["val"] + "%")


def validate_expression(expression):
    # cant have && or ||
    invalid_markers = ["&&", "||", "()", "~ &", "~&", "~ |", "~|"]
    for im in invalid_markers:
        if im in expression:
            return False

    level = 0
    for char in expression:
        if char == "(":
            level += 1
        elif char == ")":
            level -= 1

    if not level == 0:
        return False

    return True


def get_sqlalch_filter_query(expression, filter_param):
    """
    Given an advanced search expression as defined in the API docs,sl
    return an sqlalchey filter expression
    """

    expression = expression.replace("AND", "&")
    expression = expression.replace("OR", "|")
    expression = expression.replace("NOT", "~")
    expression = "(" + expression + ")"

    if not validate_expression(expression):
        raise BadRequestException("Invalid query expression")

    parse_tree = build_parse_tree(expression)
    print(parse_tree)

    query = build_query(parse_tree, filter_param)
    print(query)

    return query
