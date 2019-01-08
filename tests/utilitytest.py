from unittest import TestCase, main

from utility_standalone import decrypt_id, encrypt_id


class UtilityEncryptionTest(TestCase):

    def test_split(self):
        for inputnumber in range(-1000, 1000):
            result = decrypt_id(encrypt_id(inputnumber))
            self.assertEqual(int(result), inputnumber)


if __name__ == '__main__':
    main()
