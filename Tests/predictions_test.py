"""
    Testing of the prediction accuracy
"""
import unittest
import sys
sys.path.append('../Customer-Support-Bot-Project-main')
from bot import predict_class

class PredictionTest(unittest.TestCase):
    def test_predict_class(self):
        self.assertEqual(predict_class('hello'), [{'request': 'greeting'}])
        self.assertEqual(predict_class('hi'), [{'request': 'greeting'}])
        self.assertEqual(predict_class('Greetings'), [{'request': 'greeting'}])
        
        self.assertEqual(predict_class('Good Bye'), [{'request': 'goodbye'}])
        self.assertEqual(predict_class('Thank you, bye'), [{'request': 'goodbye'}])
        
        self.assertEqual(predict_class('Can i get the contacts of the firm?'), [{'request': 'contact_request'}])
        self.assertEqual(predict_class('How can i contact the firm?'), [{'request': 'contact_request'}])
        self.assertEqual(predict_class('I would like to contact the firm?'), [{'request': 'contact_request'}])
        
        self.assertEqual(predict_class('Do you have the injector 0442964646?'), [{'request': 'injector_availability_request'}])
        self.assertEqual(predict_class('I need the injector 0442964646?'), [{'request': 'injector_availability_request'}])
        self.assertEqual(predict_class('Is injector 0442964646 available?'), [{'request': 'injector_availability_request'}])
        
        self.assertEqual(predict_class('Can i get the details about injector 044296458646'), [{'request': 'injector_information_request'}])
        self.assertEqual(predict_class('I need information about injector 044296458646'), [{'request': 'injector_information_request'}])
        self.assertEqual(predict_class('injector 044296458646 info'), [{'request': 'injector_information_request'}])
        
        self.assertEqual(predict_class('hrgrgre'), [{'request': 'unidentified'}])
        self.assertEqual(predict_class(''), [{'request': 'unidentified'}])
        self.assertEqual(predict_class('!£$%&/'), [{'request': 'unidentified'}])

if __name__ == "__main__":
    unittest.main()
