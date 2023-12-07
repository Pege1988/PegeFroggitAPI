import unittest

from main import confidential as cf
from main import notifier as nf

class TestNotifier(unittest.TestCase):

    def test_send_mail(self):
        subject = "Pege Notifier Unittest"
        content = "Pege Notifier Unittest"
        recipient = cf.MAIL_TO_MAIN
        self.assertEqual(nf.send_mail(subject, content, recipient), "Mail sent")

if __name__ == '__main__':
    unittest.main()