#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    string utilities.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import re

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def is_merge(s, part_one, part_two):
    """Checks if the string s can be made up with part_one and
    part_two; checks if the letters are in order and if it makes up
    the whole string.

    @params:
        s: string, "Fun string checking"
        part_one: string, "Fun ring cking"
        part_two: string, "stch"
    """
    part_one = in_order_check(s, part_one)
    part_two = in_order_check(s, part_two)
    if isinstance(part_one, list) and isinstance(part_two, list):
        if len(part_one + part_two) == len(s):
            if part_one != part_two or len(part_one + part_two) == 0:
                return True
    return False

def in_order_check(s, part):
    """Return a list of indexes if in order."""
    order = list()
    for index, letter in enumerate(part):
        value = s.find(part[index])
        order.append(value)
    if order == sorted(order):
        return order

def get_namespace(name):
    """Gets the namespace from the given name.
    :param name: String to extract the namespace from.
    :return: The extracted namespace
    """
    namespace = re.match('[_0-9a-zA-Z]+(?=:)(:[_0-9a-zA-Z]+(?=:))*', name)
    if namespace:
        namespace = '%s:' % str(namespace.group(0))
    else:
        namespace = ''
    return namespace

def remove_namespace(name):
    """Removes the namespace from the given name
    :param name: The name with the namespace
    :return: The name without the namesapce
    """
    namespace = get_namespace(name)
    if namespace:
        return re.sub('^{0}'.format(namespace), '', name)
    return name

