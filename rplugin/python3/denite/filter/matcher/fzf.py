import os

from subprocess import Popen, DEVNULL, PIPE

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
            p = Popen(
                arg,
                stdin=DEVNULL,
                stdout=PIPE,
                stderr=DEVNULL,
            )
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                message = f'{fzf} is not properly installed.'
                self._throw_error(message)
                self.__disabled = True
            else:
                message = f'{fzf} could not be executed.'
                self._throw_error(message)

        stdout, _ = p.communicate('\n'.join([d['word'] for d in candidates]).encode(encoding))

        if p.returncode != 0:
            message = f'{fzf} exited with code {p.returncode}.'
            self._throw_error(message)

        return stdout.decode(encoding)

    def _throw_error(self, message):
        message = f'{self.name}: {message}'
        error(self.vim, message)
