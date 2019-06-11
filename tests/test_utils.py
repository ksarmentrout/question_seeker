import tweepy
from question_seeker import utils


class TestUtils:
    def test_aws_creds(self):
        # Loads credentials and validates against AWS validation endpoint
        auth = utils.get_auth()
        api = tweepy.API(auth)

        # This function returns a User object if the credentials are valid, False otherwise
        assert type(api.verify_credentials()) == tweepy.User

    def test_send_email(self):
        status = utils.send_email('Keep up the good work! :)')
        assert status == 200
