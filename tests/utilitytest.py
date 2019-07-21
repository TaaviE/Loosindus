from unittest import TestCase, main

from utility import get_name_in_genitive
from utility_standalone import decrypt_id, encrypt_id


class UtilityTest(TestCase):
    def test_split(self):
        for inputnumber in range(-1000, 1000):
            result = decrypt_id(encrypt_id(inputnumber))
            self.assertEqual(int(result), inputnumber)

    def test_name_lookup(self):
        assert (get_name_in_genitive("Triin") == "Triinu")



if __name__ == '__main__':
    main()
