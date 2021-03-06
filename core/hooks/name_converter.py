# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook which chooses an environment file to use based on the current context.

"""
import os
import urllib

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()

EDIT_TYPES_KEY = "edit_types"
EDITS_KEY = "edits"
VALID_EDITS = ["replace", "lower_case", "upper_case", "underscore_to_camelcase", "pad", "path_safe"]


class TemplateKeyCustom(HookBaseClass):

    def validate(self, value, validate_transforms, **kwargs):
        """
        Test if a value is valid for this key

        :param value: Value to test
        :param validate_transforms: Bool to enable validation of transforms,
                                    such as a subset calculation
        :returns: Bool
        """
        return  self.parent._validate(value, validate_transforms)


    @staticmethod
    def _underscore_to_camelcase(value):
        def camelcase():
            yield str.lower
            while True:
                yield str.capitalize

        c = camelcase()
        return "".join(c.next()(x) if x else '_' for x in value.split("_"))


    @staticmethod
    def _run_edits(edit_types, edits, value):
        """
        Runs the specified edits on this value.

        If the EDIT_TYPE_KEY(edit_type) in the TemplateKey is valid, it will apply the required "edit" on str_value.
        You can also define a set of EDITS_KEY(edits) in the TemplateKey.
        eg. use "edits" to store the replacement mapping for "replace" type "edit".
        """
        # apply the edits on the value of the key
        edits = edits or dict()
        edit_types = edit_types or list()

        # don't forget to add a new edit to VALID_EDITS
        for edit in edit_types:
            relevant_edits = dict()
            if edit in edits:
                relevant_edits = edits[edit]

            if edit in VALID_EDITS:
                if edit == "replace":
                    if relevant_edits:
                        relevant_replaces = [replace for replace in relevant_edits if replace in value]
                        for replace in relevant_replaces:
                            value = value.replace(replace, relevant_edits[replace])
                elif edit == "lower_case":
                    value = value.lower()
                elif edit == "upper_case":
                    value = value.upper()
                elif edit == "underscore_to_camelcase":
                    value = self._underscore_to_camelcase(value)
                elif edit == "pad":
                    if relevant_edits:
                        if "value" in relevant_edits:
                            padding = relevant_edits["value"]
                            value = value.zfill(padding)
                elif edit == "path_safe":
                    value = urllib.quote(value.replace(" ", "_"), safe='')

        return value
        

    def value_from_str(self, str_value, **kwargs):
        """
        Translates a string into an appropriate value for this key.

        :param str_value: The string to translate.
        :returns: The translated value.
        """
        value = self.parent._as_string(str_value)

        edit_types = kwargs.get(EDIT_TYPES_KEY)
        if edit_types:
            edits = kwargs.get(EDITS_KEY)
            value = self._run_edits(edit_types, edits, value)

        return value


    def str_from_value(self, value, **kwargs):
        """
        Converts a value into properly formatted string for this key.

        :param value: An object that will be converted to a string according to the
                      format specification.

        :returns: A string representing the formatted value.
        """
        str_value = self.parent._as_string(value)

        edit_types = kwargs.get(EDIT_TYPES_KEY)
        if edit_types:
            edits = kwargs.get(EDITS_KEY)
            str_value = self._run_edits(edit_types, edits, str_value)

        return str_value
