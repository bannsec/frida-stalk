
from ... import common

class DecompilerBase(object):
    def __init__(self, process):
        """Use this to decompile things.

        Examples:
            .. code-block:: python3

                # Attempt to get corresponding source code from address 0x12345
                process.decompiler[0x12345]
        """
        self._process = process

    @common.implement_in_engine()
    def lookup_address(self, address):
        """Lookup the corresponding decompiled code for a given address.

        Args:
            address (int): The address to look up decompiled code.

        Returns:
            revenge.plugins.decompiler.decompiled.Decompiled: Decompiled output
            or None if no corresponding decompile was found.
        """
        pass

    @common.implement_in_engine()
    def decompile_function(self, address):
        """Lookup the corresponding decompiled code for a given function.

        Args:
            address (int): The start of the function to decompile.

        Returns:
            revenge.plugins.decompiler.decompiled.Decompiled: Decompiled output
            or None if no corresponding decompile was found.
        """
        pass

    @common.validate_argument_types(item=int)
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.lookup_address(item)
