import copy, re
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError

from aplus_nodes import aplusmeta

def setup(app):
    # The AplusMeta directive is already set in aplus_setup.py:setup(app).
    # However, if one wants to use the `aplusmeta_substitutions` variable in conf.py,
    # they must also include 'meta' in the `extensions` variable in conf.py.
    # This dummy setup() function here is to suppress a Sphinx warning:
    # "extension 'meta' has no setup() function; is it really a Sphinx
    # extension module?"
    #
    # See the section "5. Meta (exercise round settings)" in README.md.
    pass


class AplusMeta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'open-time': directives.unchanged,
        'read-open-time': directives.unchanged,
        'close-time': directives.unchanged,
        'late-time': directives.unchanged,
        'late-penalty': directives.unchanged,
        'audience': directives.unchanged,
        'hidden': directives.flag,
        'points-to-pass': directives.nonnegative_int, # set points to pass for modules
        'introduction': directives.unchanged, # module introduction HTML
    }

    # Valid date formats:
    # 1. 'YYYY-MM-DD [hh[:mm[:ss]]]'
    # 2. 'DD.MM.YYYY [hh[:mm[:ss]]]'
    date_format = re.compile(r"^(\d\d\d\d-\d\d-\d\d|\d\d.\d\d.\d\d\d\d)( \d\d(:\d\d(:\d\d)?)?)?$")

    # Keys in option_spec which require a date format
    date_format_required = {
        'open-time', 'read-open-time', 'close-time', 'late-time'
    }

    def run(self):
        env = self.state.document.settings.env
        aplusmeta_substitutions = env.config.aplusmeta_substitutions
        modified_options = copy.deepcopy(self.options)

        # Substitute values of options if a corresponding string is found in
        # the configuration variable aplusmeta_substitutions (set in conf.py).
        # Example:
        #     self.options['open-time'] == 'open01'
        #     aplusmeta_substitutions['open01'] == '2020-01-03 12:00'
        #     # Result
        #     modified_options['open-time'] = '2020-01-03 12:00'
        #
        # See the section "5. Meta (exercise round settings)" in README.md.
        for opt, value in self.options.items():
            if opt in AplusMeta.date_format_required:
                self.validate_time(opt, value, aplusmeta_substitutions)
            if value in aplusmeta_substitutions:
                modified_options[opt] = aplusmeta_substitutions[value]
        return [aplusmeta(options=modified_options)]

    def validate_time(self, opt, value, aplusmeta_substitutions):
        # Validates the time of given option-value pair. Also checks possible
        # substitutions in the configuration variable 'aplusmeta_substitutions'.
        # Raises a SphinxError if value is invalid (even with substitution).
        source, line = self.state_machine.get_source_and_line(self.lineno)
        position_text = ("{}, line {}, directive aplusmeta:\n" +
                         "option '{}' has value '{}' ")
        date_text = ("1. Date in format 'YYYY-MM-DD [hh[:mm[:ss]]]', e.g. " +
                    "'2020-01-16 16:00'\n" +
                    "2. Date in format 'DD.MM.YYYY [hh[:mm[:ss]]]', e.g. " +
                    "'16.01.2020 16:00'\n")
        is_time = AplusMeta.date_format.match
        if not is_time(value):
            if value not in aplusmeta_substitutions:
                raise SphinxError((position_text +
                    "which was not recognised.\n" +
                    "This should be one of:\n" + date_text +
                    "3. A substitution text in aplusmeta_substitutions in conf.py; " +
                    "see A-plus RST tools README.md > Meta (exercise round settings)"
                    ).format(source, line, opt, value))
            else:
                if not is_time(aplusmeta_substitutions[value]):
                    raise SphinxError((position_text +
                        "which substitutes to " +
                        "invalid value '{}' This should be either:\n" +
                        date_text +
                        "Probable cause: incorrect field in the variable " +
                        "`aplusmeta_substitutions` in the file conf.py."
                        ).format(source, line, opt, value, aplusmeta_substitutions[value]))
