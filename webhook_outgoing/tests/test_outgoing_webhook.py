import odoo.tests
from odoo.tests.common import TransactionCase
from odoo.tools import ustr


@odoo.tests.tagged("post_install", "-at_install")
class TestOutgoingWebhook(TransactionCase):
    def test_01_trigger_webhook(self):
        test_automation = self.env["base.automation"].create(
            {
                "name": "Test outgoing webhook on updated partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "type": "ir.actions.server",
                "trigger": "on_create_or_write",
                "trigger_field_ids": [
                    (6, 0, [self.env.ref("base.field_res_partner__name").id])
                ],
                "state": "custom_webhook",
                "endpoint": "https://httpbin.org/post",
                "request_method": "post",
                "request_type": "request",
                "log_webhook_calls": True,
                "body_template": '{"name": "{{record.name}}", "email": "{{record.email}}"}',
            }
        )
        test_partner_1 = self.env["res.partner"].create(
            {"name": "Test Partner 1", "email": "test.partner1@test.example.com"}
        )
        log = self.env["webhook.logging"].search(
            [("webhook", "ilike", "Test outgoing webhook on updated partner")], limit=1
        )
        self.assertTrue(log)
        self.assertEqual(
            log.body,
            ustr(
                '{"name": "Test Partner 1", "email": "test.partner1@test.example.com"}'
            ),
        )

        test_partner_1.name = "Test Partner 1-1"
        log = self.env["webhook.logging"].search(
            [("webhook", "ilike", "Test outgoing webhook on updated partner")], limit=1
        )
        self.assertEqual(
            log.body,
            ustr(
                '{"name": "Test Partner 1-1", "email": "test.partner1@test.example.com"}'
            ),
        )

        test_automation.unlink()
        self.env["webhook.logging"].search([]).unlink()

    def test_02_render_request_body(self):
        test_automation = self.env["base.automation"].create(
            {
                "name": "Test outgoing webhook",
                "model_id": self.env.ref("base.model_res_partner").id,
                "type": "ir.actions.server",
                "trigger": "on_create_or_write",
                "trigger_field_ids": [
                    (6, 0, [self.env.ref("base.field_res_partner__name").id])
                ],
                "state": "custom_webhook",
                "endpoint": "https://httpbin.org/post",
                "request_method": "post",
                "request_type": "request",
                "log_webhook_calls": False,
                "active": True,
                "body_template": '{"name": "{{record.name}}", "email": "{{record.email}}"}',
            }
        )
        webhook_action = test_automation.action_server_id
        test_partner_2 = self.env["res.partner"].create(
            {"name": "Test Partner 2", "email": "test.partner2@test.example.com"}
        )
        body_string = webhook_action._prepare_data_for_post_request(test_partner_2, {})
        self.assertEqual(
            body_string,
            (b'{"name": "Test Partner 2", "email": "test.partner2@test.example.com"}'),
        )
        test_automation.unlink()
