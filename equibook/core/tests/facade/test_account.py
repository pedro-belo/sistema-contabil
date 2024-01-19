from equibook.core.tests import base
from equibook.core import facade


class CreateAccountTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_create_account(self):
        root = facade.Account.objects.get_asset(self.user)

        acc1 = facade.create_account(
            self.user, parent=root, form_data={"name": "ACC-1"}
        )
        self.assertIsNotNone(acc1.id)
        self.assertEqual(acc1.name, "ACC-1")
        self.assertEqual(acc1.balance_type, root.balance_type)
        self.assertEqual(acc1.account_type, facade.TypeOfAccount.SUBDIVISION)
        self.assertEqual(acc1.root_type, root.account_type)
        self.assertEqual(acc1.parent, root)
        self.assertEqual(acc1.user, self.user)

        ac2 = facade.create_account(self.user, parent=acc1, form_data={"name": "ACC-2"})
        self.assertEqual(ac2.root_type, acc1.root_type)
        self.assertEqual(ac2.parent, acc1)

    def test_create_account_using_parent_none(self):
        with self.assertRaises(ValueError):
            facade.create_account(self.user, parent=None, form_data={"name": "name"})
