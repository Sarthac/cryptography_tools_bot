"""
This module implements various substitution ciphers.

The base class, SubstitutionCipher, provides the fundamental framework for creating substitution ciphers.
It handles the mapping of an alphabet to a cipher alphabet, and the core ciphering and deciphering logic.

The following ciphers are implemented:
- MixedAlphabet: A substitution cipher with a mixed alphabet generated from a keyword.
- Atbash: A simple substitution cipher where the alphabet is reversed.
- SimpleSubstitution: A substitution cipher with a randomly generated or user-defined cipher alphabet.
- Rotate: A substitution cipher that rotates the alphabet by a given shift.
- Caesar: A specific instance of the Rotate cipher with a shift of 3.
- Rot13: A specific instance of the Rotate cipher with a shift of 13.
- Baconian: A substitution cipher that uses a 5-character binary representation for each letter.
- PolybiusSquare: A substitution cipher that uses a 5x5 grid to represent each letter.
"""

import string, random


class SubstitutionCipher:
    """
    A base class for creating substitution ciphers.

    This class provides the core functionality for substitution ciphers, including
    creating a mapping between the standard alphabet and a cipher alphabet, and
    methods for encrypting and decrypting text.
    """

    def __init__(self, cipher_alphabets: list) -> None:
        """
        Initializes the SubstitutionCipher.

        Args:
            cipher_alphabets: A list of characters representing the cipher alphabet.
        """
        self.cipher_alphabets = cipher_alphabets
        self.mapping = self.cipher_mapping()

    # creating mapping of alphanets to cipher_alphanets
    # examples : for atbash cipher
    # 'a' : 'z'
    # 'b' : 'y'
    # 'c' : 'x'

    def cipher_mapping(self):
        """
        Creates a mapping from the standard alphabet to the cipher alphabet.

        Returns:
            A dictionary containing separate mappings for lowercase and uppercase letters.
        """
        mapping = {"lowercase": {}, "uppercase": {}}
        for i, val in enumerate(string.ascii_lowercase):
            mapping["lowercase"][val] = self.cipher_alphabets[i]
            mapping["uppercase"][val.upper()] = self.cipher_alphabets[i].upper()

        return mapping

    def cipher(self, text: str) -> str:
        """
        Encrypts the given text using the substitution cipher.

        Args:
            text: The text to be encrypted.

        Returns:
            The encrypted text.
        """
        cipher_text = ""
        for letter in text:
            if letter.islower():
                cipher_text += self.mapping["lowercase"].get(
                    letter, letter
                )  # two letter parameters because if the letter doesn't include in the mapping, it will fallback to default i.e second letter parameter which is original letter
            elif letter.isupper():
                cipher_text += self.mapping["uppercase"].get(letter, letter)
            else:
                cipher_text += letter
        return cipher_text

    def decipher(self, text: str) -> str:
        """
        Decrypts the given text using the substitution cipher.

        Args:
            text: The text to be decrypted.

        Returns:
            The decrypted text.
        """
        # Reverse the mapping for both cases
        inverse_lower = {v: k for k, v in self.mapping["lowercase"].items()}
        inverse_upper = {v: k for k, v in self.mapping["uppercase"].items()}

        plain_text = ""
        for letter in text:
            if letter.islower():
                plain_text += inverse_lower.get(letter, letter)
            elif letter.isupper():
                plain_text += inverse_upper.get(letter, letter)
            else:
                plain_text += letter
        return plain_text


class MixedAlphabet(SubstitutionCipher):
    """
    A substitution cipher with a mixed alphabet generated from a keyword.

    The cipher alphabet is created by taking the unique letters of the keyword,
    followed by the remaining letters of the alphabet in their normal order.
    """

    def __init__(self, keyword: str) -> None:
        """
        Initializes the MixedAlphabet cipher.

        Args:
            keyword: The keyword to use for generating the cipher alphabet.
        """
        self.keyword = keyword
        cipher_alphabets = self.mixed_cipher_alphabets()
        super().__init__(cipher_alphabets)

    def mixed_cipher_alphabets(self):
        """
        Generates the mixed cipher alphabet from the keyword.

        Returns:
            A list of characters representing the mixed cipher alphabet.
        """
        # Make keyword unique while preserving order
        unique_keyword = list(dict.fromkeys(self.keyword))

        alphabets = string.ascii_lowercase
        cipher_alphabet = unique_keyword

        for letter in alphabets:
            if letter not in cipher_alphabet:
                cipher_alphabet.append(letter)

        return cipher_alphabet


class Atbash(SubstitutionCipher):
    """
    A simple substitution cipher where the alphabet is reversed.

    'a' becomes 'z', 'b' becomes 'y', and so on.
    """

    def __init__(self) -> None:
        """
        Initializes the Atbash cipher.
        """
        reverse_lowercase = list(string.ascii_lowercase[::-1])
        super().__init__(reverse_lowercase)


class SimpleSubstitution(SubstitutionCipher):
    """
    A substitution cipher with a randomly generated or user-defined cipher alphabet.
    """

    def __init__(self, cipher_alphabets: str | None = None) -> None:
        """
        Initializes the SimpleSubstitution cipher.

        Args:
            cipher_alphabets: A 26-character string representing the cipher alphabet.
                If None, a random cipher alphabet is generated.
        """
        if cipher_alphabets is None:
            cipher_alphabets_list = self.generate_cipher_alphabets()
        else:
            cipher_alphabets_lower = cipher_alphabets.lower()

            if len(cipher_alphabets_lower) != 26 or set(cipher_alphabets_lower) != set(
                string.ascii_lowercase
            ):
                raise ValueError("cipher_alphabets must be a-z and 26 char long")

            cipher_alphabets_list = list(cipher_alphabets_lower)

        self.cipher_alphabets = cipher_alphabets_list
        super().__init__(self.cipher_alphabets)

    @staticmethod
    def generate_cipher_alphabets():
        """
        Generates a random cipher alphabet.

        Returns:
            A list of characters representing the random cipher alphabet.
        """
        return random.sample(string.ascii_lowercase, k=26)


class Rotate(SubstitutionCipher):
    """
    A substitution cipher that rotates the alphabet by a given shift.
    """

    def __init__(self, shift: int) -> None:
        """
        Initializes the Rotate cipher.

        Args:
            shift: The number of positions to rotate the alphabet.
        """
        self.shift = shift
        cipher_alphabets = self.shift_to()
        super().__init__(cipher_alphabets)

    def shift_to(self):
        """
        Rotates the alphabet by the given shift.

        Returns:
            A list of characters representing the rotated alphabet.
        """
        # small letter in ASCII start from 97, in ASCII a = 97
        return [
            chr((ord(char) - 97 + self.shift) % 26 + 97)
            for char in string.ascii_lowercase
        ]


class Caesar(Rotate):
    """
    A specific instance of the Rotate cipher with a shift of 3.
    """

    def __init__(self, shift: int = 3) -> None:
        """
        Initializes the Caesar cipher.

        Args:
            shift: The number of positions to rotate the alphabet (default is 3).
        """
        super().__init__(shift)


class Rot13(Rotate):
    """
    A specific instance of the Rotate cipher with a shift of 13.
    """

    def __init__(self, shift: int = 13) -> None:
        """
        Initializes the Rot13 cipher.

        Args:
            shift: The number of positions to rotate the alphabet (default is 13).
        """
        super().__init__(shift)


class Shift(Rotate):
    """
    A specific instance of the Rorate cipher with a user defined shift
    """

    def __init__(self, shift: int) -> None:
        """
        Initializes the Shift cipher.

        Args:
            shift: The number of positions to rotate the alphabet.
        """
        super().__init__(shift)


class Baconian(SubstitutionCipher):
    """
    A substitution cipher that uses a 5-character binary representation for each letter.
    """

    modern_baconian_cipher = [
        "aaaaa",  # a
        "aaaab",  # b
        "aaaba",  # c
        "aaabb",  # d
        "aabaa",  # e
        "aabab",  # f
        "aabba",  # g
        "aabbb",  # h
        "abaaa",  # i
        "abaab",  # j
        "ababa",  # k
        "ababb",  # l
        "abbaa",  # m
        "abbab",  # n
        "abbba",  # o
        "abbbb",  # p
        "baaaa",  # q
        "baaab",  # r
        "baaba",  # s
        "baabb",  # t
        "babaa",  # u
        "babab",  # v
        "babba",  # w
        "babbb",  # x
        "bbaaa",  # y
        "bbaab",  # z
    ]

    old_baconian_cipher = [
        "aaaaa",  # A
        "aaaab",  # B
        "aaaba",  # C
        "aaabb",  # D
        "aabaa",  # E
        "aabab",  # F
        "aabba",  # G
        "aabbb",  # H
        "abaaa",  # I / J
        "abaaa",  # I / J
        "abaab",  # K
        "ababa",  # L
        "ababb",  # M
        "abbaa",  # N
        "abbab",  # O
        "abbba",  # P
        "abbbb",  # Q
        "baaaa",  # R
        "baaab",  # S
        "baaba",  # T
        "baabb",  # U / V
        "baabb",  # U / V
        "babaa",  # W
        "babab",  # X
        "babba",  # Y
        "babbb",  # Z
    ]

    def __init__(self, modern_implementation=True) -> None:
        """
        Initializes the Baconian cipher.

        Args:
            modern_implementation: Whether to use the modern or old implementation of the cipher.
        """
        cipher_alphabet = None
        if modern_implementation:
            cipher_alphabet = self.modern_baconian_cipher
        else:
            cipher_alphabet = self.old_baconian_cipher

        super().__init__(cipher_alphabet)

    def decipher(self, text: str) -> str:
        """
        Decrypts the given text using the Baconian cipher.

        Args:
            text: The text to be decrypted.

        Returns:
            The decrypted text.
        """
        inverse_lower = {v: k for k, v in self.mapping["lowercase"].items()}
        inverse_upper = {v: k for k, v in self.mapping["uppercase"].items()}
        plain_text = ""
        i = 0
        word_length = 5
        while i < len(text):
            if text[i] in [" ", "\n", "\t"]:  # You can expand this list for more
                plain_text += text[i]
                i += 1
            else:
                block = text[i : i + word_length]
                if block[0].islower():
                    plain_text += inverse_lower.get(block, "?")
                else:
                    plain_text += inverse_upper.get(block, "?")
                i += word_length
        return plain_text


class PolybiusSquare(SubstitutionCipher):
    """
    A substitution cipher that uses a 5x5 grid to represent each letter.
    """

    cipher_alphabets = [
        "00",
        "01",
        "02",
        "03",
        "04",
        "10",
        "11",
        "12",
        "13",
        "14",
        "20",
        "21",
        "22",
        "23",
        "24",
        "30",
        "31",
        "32",
        "33",
        "34",
        "40",
        "41",
        "42",
        "43",
        "44",
        "51",
    ]

    def __init__(self) -> None:
        """
        Initializes the PolybiusSquare cipher.
        """
        super().__init__(self.cipher_alphabets)

    def cipher(self, text: str) -> str:
        """
        Encrypts the given text using the PolybiusSquare cipher.

        Args:
            text: The text to be encrypted.

        Returns:
            The encrypted text.
        """
        cipher_text = ""
        for letter in text:
            if letter.islower():
                cipher_text += self.mapping["lowercase"].get(
                    letter, letter
                )  # two letter parameters because if the letter doesn't include in the mapping, it will fallback to default i.e second letter parameter which is original letter
            elif letter.isupper():
                cipher_text += self.mapping["uppercase"].get(letter, letter)
            elif letter.isnumeric():
                cipher_text += ""
            else:
                cipher_text += letter
        return cipher_text

    def decipher(self, text: str) -> str:
        """
        Decrypts the given text using the PolybiusSquare cipher.

        Args:
            text: The text to be decrypted.

        Returns:
            The decrypted text.
        """
        inverse_lower = {v: k for k, v in self.mapping["lowercase"].items()}
        inverse_upper = {v: k for k, v in self.mapping["uppercase"].items()}
        plain_text = ""
        i = 0
        word_length = 2
        while i < len(text):
            if text[i] in [" ", "\n", "\t"]:  # You can expand this list for more
                plain_text += text[i]
                i += 1
            else:
                block = text[i : i + word_length]
                plain_text += inverse_lower.get(block, "?")
                i += word_length
        return plain_text



