from .utils import omit_all_except_alpha


class ColumnarTransposition:
    def __init__(self, key: str):
        self.key = key.upper()

    def _get_key_order(self):
        """Return list of column indices in the order they should be read."""
        return sorted(range(len(self.key)), key=lambda i: (self.key[i], i))

    def _create_grid(self, text: str):
        key_len = len(self.key)
        row_len = -(-len(text) // key_len)  # ceil division
        return [["" for _ in range(key_len)] for _ in range(row_len)]

    def cipher(self, plaintext: str):
        plaintext = omit_all_except_alpha(plaintext).upper()
        grid = self._create_grid(plaintext)
        # Fill grid row-by-row
        idx = 0
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                if idx < len(plaintext):
                    grid[r][c] = plaintext[idx]
                    idx += 1

        # Read columns in key order
        ciphertext = ""
        for c in self._get_key_order():
            for r in range(len(grid)):
                if grid[r][c] != "":
                    ciphertext += grid[r][c]
        return ciphertext

    def decipher(self, ciphertext: str):
        plaintext = omit_all_except_alpha(ciphertext).upper()
        grid = self._create_grid(ciphertext)
        order = self._get_key_order()

        idx = 0
        # Fill columns in key order
        for c in order:
            for r in range(len(grid)):
                if idx < len(ciphertext):
                    grid[r][c] = ciphertext[idx]
                    idx += 1

        # Read rows to reconstruct plaintext
        plaintext = ""
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                if grid[r][c] != "":
                    plaintext += grid[r][c]
        return plaintext
