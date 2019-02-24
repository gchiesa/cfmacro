#!/usr/bin/env python
import logging
import json
import re
import sys

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

logging.basicConfig(level=logging.INFO)


def cf_pprint(template_json: str) -> str:
    def reformat(matchobj):
        name = matchobj.group(1)
        value = matchobj.group(2)
        value = value.replace('\n', '')
        value = ' '.join(value.split())
        return f'{{ {name}: {value} }}'

    data = json.loads(template_json)
    output = json.dumps(data, indent=4)

    beautifiers = [
        # ref
        {
            'search': r'\{[ \t]*\n[ \t]*(\"Ref\")[ \t]*\:[ \t]*(\"\w.*\")[ \t]*\n[ \t]*\}',
            'replace': r'{ \1: \2 }',
            'flags': re.MULTILINE
         },
        # Fn::<something>
        {
            'search': r'\{[ \t]*\n[ \t]*(\"Fn::[a-zA-Z].*?\")[ \t]*\:[ \t](\[.*?\])[ \t]*\n[ \t]*\}',
            'replace': reformat,
            'flags': re.DOTALL
        }
    ]
    # ref
    for b in beautifiers:
        output = re.sub(b['search'], b['replace'],
                        output, 0, b['flags'])
    return output


def main():
    logger = logging.getLogger(__file__)
    data = sys.stdin.read()
    try:
        processed = cf_pprint(data)
    except ValueError as e:
        logger.error(f'Unable to reformat the file. Error: {str(e)}')
        sys.exit(1)
    print(processed)


if __name__ == '__main__':
    main()
