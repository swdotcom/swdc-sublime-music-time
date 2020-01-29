# TEST case for checking client credentials for spotify

import unittest
from cred import get_credentials

# Pass ids to check function
client_id = "eb67e22ba1c6474aad8ec8067480d9dc"
client_secret = "2b40b4975b2743189c87f4712c0cd59e"

class ClientCredentialTest(unittest.TestCase):
    '''
    Check client credentials

    ''' 
    def test_client_id(self):         
        self.assertEqual(get_credentials()[0], client_id, msg = "Client id match not found !")

    def test_client_secret(self):         
        self.assertEqual(get_credentials()[1], client_secret, msg = "Client secret match not found !") 
  
if __name__ == '__main__': 
    unittest.main() 