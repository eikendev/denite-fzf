import os

from subprocess import Popen, PIPE

from denite.base.filter import Base
from denite.util import error, convert2fuzzy_pattern


class Filter(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/fzf'
        self.description = 'fzf matcher'

        self.__disabled = False

    def filter(self, context):
        if not context['candidates'] or not context['input'] or self.__disabled:
            return context['candidates']

        if self.__disabled:
            return []

        fzf = '.exe' if context['is_windows'] else ''
        fzf = 'fzf' + fzf

        result = self._get_result(
            fzf,
            context['candidates'],
            context['encoding'],
            context['input'],
        )

        return [x for x in context['candidates'] if x['word'] in result]

    def convert_pattern(self, input_str):
        return convert2fuzzy_pattern(input_str)

    def _get_result(self, fzf, candidates, encoding, pattern):
        arg = [fzf, '+s', '-f', pattern]

        try:
            p = Popen(arg, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                error(self.vim, 'matcher/fzf: ' + fzf + ' is not properly installed.')
                self.__disabled = True
            else:
                error(self.vim, 'matcher/fzf: cannot execute ' + fzf + '.')

        (stdout, stderr) = p.communicate('\n'.join([d['word'] for d in candidates]).encode(encoding))

        if stderr:
            error(self.vim, 'matcher/fzf: ' + '\n'.join(stderr))

        return stdout.decode(encoding)