import unittest


class RegistryTests(unittest.TestCase):
    def test_builtin_apps_have_chinese_labels_and_categories(self):
        from oai_bridge.registry import filter_apps, merge_apps

        apps = merge_apps()
        image_labels = [app["label"] for app in filter_apps(apps, "image")]
        video_labels = [app["label"] for app in filter_apps(apps, "video")]

        self.assertIn("Banana 生图", image_labels)
        self.assertIn("Qwen 编辑图像", image_labels)
        self.assertNotIn("文生视频", video_labels)
        self.assertNotIn("图生视频", video_labels)
        self.assertEqual(video_labels, ["Seedance 视频"])

    def test_dynamic_apps_extend_builtin_registry(self):
        from oai_bridge.registry import filter_apps, merge_apps

        apps = merge_apps(
            [
                {
                    "id": "new-video",
                    "alias": "新视频模型",
                    "category": "video",
                    "mode": "task_submit",
                    "output": "video",
                }
            ]
        )

        self.assertIn("新视频模型", [app["label"] for app in filter_apps(apps, "video")])


if __name__ == "__main__":
    unittest.main()
