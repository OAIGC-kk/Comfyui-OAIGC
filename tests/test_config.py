import tempfile
import unittest
from pathlib import Path


class ConfigTests(unittest.TestCase):
    def test_hardcoded_backend_urls_use_working_oaigc_api_host(self):
        from oai_bridge import config

        self.assertEqual(config.HARDCODED_BASE_URL, "https://oaigc.cn/api")
        self.assertEqual(config.HARDCODED_UPLOAD_URL, "https://oaigc.cn/api/file/tool/upload")
        self.assertNotIn("api.oaigc.cn", config.HARDCODED_BASE_URL)

    def test_token_is_masked_in_public_config_without_backend_urls(self):
        from oai_bridge.config import OAIConfig

        cfg = OAIConfig(base_url="https://api.example.test", token="abcd1234wxyz")

        self.assertEqual(
            cfg.to_public_dict(),
            {
                "has_token": True,
                "token_masked": "abcd****wxyz",
                "poll_interval": 3.0,
                "poll_timeout": 900.0,
            },
        )

    def test_load_config_accepts_utf8_bom_file(self):
        from oai_bridge import config

        with tempfile.TemporaryDirectory() as tmp:
            original_config_path = config.CONFIG_PATH
            config.CONFIG_PATH = Path(tmp) / "config.json"
            try:
                config.CONFIG_PATH.write_text('{"token":"secret-token"}', encoding="utf-8-sig")
                loaded = config.load_config()
            finally:
                config.CONFIG_PATH = original_config_path

        self.assertEqual(loaded.token, "secret-token")


    def test_save_and_load_config_round_trip_ignores_backend_urls(self):
        from oai_bridge import config

        with tempfile.TemporaryDirectory() as tmp:
            original_data_dir = config.DATA_DIR
            original_config_path = config.CONFIG_PATH
            config.DATA_DIR = Path(tmp)
            config.CONFIG_PATH = Path(tmp) / "config.json"
            try:
                config.save_config(
                    {
                        "base_url": "https://evil.example/api",
                        "upload_url": "https://evil.example/upload",
                        "token": "secret-token",
                        "poll_interval": 1.5,
                    }
                )

                loaded = config.load_config()
            finally:
                config.DATA_DIR = original_data_dir
                config.CONFIG_PATH = original_config_path

        self.assertEqual(loaded.base_url, config.HARDCODED_BASE_URL)
        self.assertEqual(loaded.upload_url, config.HARDCODED_UPLOAD_URL)
        self.assertEqual(loaded.token, "secret-token")
        self.assertEqual(loaded.poll_interval, 1.5)
        self.assertEqual(loaded.poll_timeout, 900.0)


if __name__ == "__main__":
    unittest.main()
