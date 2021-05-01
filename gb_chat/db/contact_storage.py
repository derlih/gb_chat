from typing import List

from sqlalchemy.orm.session import Session

from .tables import User


class ContactError(ValueError):
    pass


class ContactStorage:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_contact(self, owner: User, contact: User) -> None:
        if owner is contact:
            raise ContactError("Can't add self to contacts")

        if contact in owner.contacts:
            return

        owner.contacts.append(contact)
        self._session.commit()

    def remove_contact(self, owner: User, contact: User) -> None:
        try:
            owner.contacts.remove(contact)
        except ValueError:
            return

        self._session.commit()

    def get_user_contacts(self, owner: User) -> List[User]:
        return owner.contacts
