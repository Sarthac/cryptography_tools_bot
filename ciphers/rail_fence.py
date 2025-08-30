from .utils import omit_blank_spaces, omit_all_except_alpha


class RailFence:
    def __init__(self, s: str, row_length: int = 3, str_validation="omit_all") -> None:
        if row_length < 2:
            raise ValueError("row_length must be at least 2")
        if str_validation == "omit_spaces":
            self.s = omit_blank_spaces(s).upper()
        else:
            self.s = omit_all_except_alpha(s).upper()

        self.row_length = row_length

    def create_pattern(self):
        """boolean pattern to mark letter positions."""
        s_length = len(self.s)
        rails = [[None for _ in range(s_length)] for _ in range(self.row_length)]

        row = 0
        direction = 1
        for col in range(s_length):
            rails[row][col] = True
            row += direction
            if row == self.row_length - 1 or row == 0:
                direction *= -1
        return rails

    def create_rail_fence(self):
        """Fill zigzag pattern with characters for encryption."""
        s_length = len(self.s)
        rails = [[None for _ in range(s_length)] for _ in range(self.row_length)]

        row = 0
        direction = 1
        for col, ch in enumerate(self.s):
            rails[row][col] = ch
            row += direction
            if row == self.row_length - 1 or row == 0:
                direction *= -1
        return rails

    def cipher(self, rail_matrix: list):
        """Read row-by-row to get encrypted string."""
        out = []
        for row in rail_matrix:
            for ch in row:
                if ch is not None:
                    out.append(ch)
        return "".join(out)

    def decipher(self):
        """Reverse the encryption process, returning the plaintext."""
        s_len = len(self.s)
        if self.row_length < 2 or s_len == 0:
            return self.s  # identity cases

        # Step 1: Build mask of positions in zigzag
        mask = self.create_pattern()

        # Step 2: Fill row-by-row with the encrypted text
        filled = [[None for _ in range(s_len)] for _ in range(self.row_length)]
        idx = 0
        for r in range(self.row_length):
            for c in range(s_len):
                if mask[r][c]:
                    filled[r][c] = self.s[idx]
                    idx += 1

        # Step 3: Read in zigzag order to reconstruct plaintext
        row = 0
        direction = 1
        out = []
        for c in range(s_len):
            out.append(filled[row][c])
            row += direction
            if row == self.row_length - 1 or row == 0:
                direction *= -1

        return "".join(out)
