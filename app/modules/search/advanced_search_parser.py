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


def build_query(parse_tree, cluster):
    """
    Given a parse tree, build an sqlalchemy nested query using or_ and and_ functions
    """
    OPERATORS = {"&": and_, "|": or_, "~": not_}

    if "left" in parse_tree and "right" in parse_tree:
        operator = OPERATORS[parse_tree["val"]]
        return_val = operator(
            build_query(parse_tree["left"], cluster),
            build_query(parse_tree["right"], cluster),
        )

        return return_val
    elif not "val" in parse_tree and "left" in parse_tree:
        return build_query(parse_tree["left"], cluster)

    elif not "left" in parse_tree and "right" in parse_tree:
        operator = OPERATORS[parse_tree["val"]]
        return operator(build_query(parse_tree["right"], cluster))

    else:
        val = parse_tree["val"]

        if not "[" in val or not "]" in val:
            val = val + " [title, description]"

        search_in = val[val.index("[") + 1 : val.index("]")]
        search_in = [s.strip() for s in search_in.split(",")]
        val = val.split("[")[0].strip()

        search_in_funcs = []
        if "title" in search_in:
            search_in_funcs.append(Article.title.like(f"%{val}%"))
        if "description" in search_in:
            search_in_funcs.append(Article.description.like(f"%{val}%"))
        if "content" in search_in:
            search_in_funcs.append(Article.content.like(f"%{val}%"))

        if cluster:
            return Cluster.articles.any(or_(*search_in_funcs))
        else:
            return or_(*search_in_funcs)


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


def get_sqlalch_filter_query(expression, cluster=False):
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

    query = build_query(parse_tree, cluster)

    return query
