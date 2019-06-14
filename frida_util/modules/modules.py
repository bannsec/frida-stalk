
import logging
logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)

from prettytable import PrettyTable
from fnmatch import fnmatch

class Modules(object):

    def __init__(self, util):
        self._util = util

    def __iter__(self):
        return self.modules.__iter__()

    def __len__(self):
        return len(self.modules)

    def __repr__(self):
        attrs = ['Modules', str(len(self))]
        return "<{}>".format(' '.join(attrs))

    def __str__(self):
        table = PrettyTable(['name', 'base', 'size', 'path'])

        for module in self:
            table.add_row([module.name, hex(module.base), hex(module.size), module.path])

        table.align['path'] = 'l'
        
        return str(table)

    def __getitem__(self, item):

        if isinstance(item, str):
            return next(mod for mod in self if fnmatch(mod.name, item))

        raise NotImplementedError

    @property
    def modules(self):
        """list: Return list of modules."""
        mods = self._util.run_script_generic("""send(Process.enumerateModulesSync());""", raw=True, unload=True)[0][0]
        return [Module(self._util, name=mod['name'], base=mod['base'], size=mod['size'], path=mod['path']) for mod in mods]

from .module import Module