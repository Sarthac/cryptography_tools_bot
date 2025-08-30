from .columnar_transposition import ColumnarTransposition


class Scytale(ColumnarTransposition):
    def __init__(self, key: int = 3) -> None:
        self.key = key

    def _create_grid(self, text: str):
        column_len = self.key
        row_len = -(-len(text) // self.key)  # ceil division
        return [["" for _ in range(column_len)] for _ in range(row_len)]

    def _get_key_order(self):
        return range(self.key)

    def cipher(self, plaintext: str):
        if self.key >= len(plaintext) // 2:
            raise ValueError("Key should be less than half size of text")
        else:
            return super().cipher(plaintext)
