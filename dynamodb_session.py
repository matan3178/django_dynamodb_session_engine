import boto3
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.contrib.sessions.backends.base import CreateError, SessionBase

ID_ATTR = settings.DYNAMODB_SESSIONS_ATTR_ID
TTL_ATTR = settings.DYNAMODB_SESSIONS_ATTR_TTL
SESSION_DATA_ATTR = settings.DYNAMODB_SESSIONS_ATTR_SESSION_DATA


def get_dynamodb():
    if settings.APP_ENV == 'local':
        return boto3.resource('dynamodb', endpoint_url=settings.DYNAMODB_LOCAL_ENDPOINT)
    else:
        return boto3.resource('dynamodb', region_name=settings.DYNAMODB_REGION)


class SessionStore(SessionBase):
    """
    Implement DynamoDB session store.
    """

    def __init__(self, session_key=None):
        super().__init__(session_key)
        self.dynamodb = get_dynamodb()
        self.session_table = self.dynamodb.Table(settings.DYNAMODB_SESSIONS_TABLE)

    def _get_session_from_db(self):
        if self.session_key is None:
            return

        session = self.session_table.get_item(Key={ID_ATTR: self.session_key})
        if 'Item' not in session or session['Item'][TTL_ATTR] <= datetime.now().timestamp():
            self._session_key = None
            return

        return session['Item']

    def load(self):
        session = self._get_session_from_db()
        if session is None:
            return {}
        return self.decode(session[SESSION_DATA_ATTR])

    def exists(self, session_key):
        if self.session_key is None:
            return False

        return 'Item' in self.session_table.get_item(Key={ID_ATTR: self.session_key})

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        """
        Save the current session data to the database. If 'must_create' is
        True, raise a database error if the saving operation doesn't create a
        new entry (as opposed to possibly updating an existing entry).
        """
        if self.session_key is None:
            return self.create()

        session_data = self._get_session(no_load=must_create)
        if must_create:
            try:
                self.session_table.put_item(
                    Item={
                        ID_ATTR: self._get_or_create_session_key(),
                        SESSION_DATA_ATTR: self.encode(session_data),
                        TTL_ATTR: Decimal(self.get_expiry_date().timestamp())
                    },
                    ConditionExpression='attribute_not_exists(id)'
                )
            except Exception:
                raise CreateError

        else:
            self.session_table.update_item(Key={ID_ATTR: self._get_or_create_session_key()},
                                           AttributeUpdates={
                                               SESSION_DATA_ATTR: {'Value': self.encode(session_data)},
                                               TTL_ATTR: {'Value': Decimal(self.get_expiry_date().timestamp())}
                                           })

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.session_table.delete_item(Key={ID_ATTR: session_key})
        except Exception:
            pass

    @classmethod
    def clear_expired(cls):
        pass  # Dynamodb will do it by itself using the TTL
