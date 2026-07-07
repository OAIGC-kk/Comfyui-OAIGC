import unittest
from unittest.mock import patch


class FakeClient:
    def __init__(self):
        self.polls = 0

    async def banana_generate(self, payload):
        return {"code": 200, "data": {"imageUrl": "https://example.test/image.png"}}

    async def submit_task(self, app_id, parameter):
        return {"code": 200, "data": {"taskId": "task-1"}}

    async def query_task(self, task_id):
        self.polls += 1
        if self.polls == 1:
            return {"code": 200, "data": {"status": "queued", "task_id": task_id, "result": ""}}
        return {
            "code": 200,
            "data": {"status": "success", "task_id": task_id, "result": "https://example.test/result.png"},
        }

    async def seedance_create(self, payload):
        return {"code": 200, "data": {"task_id": "seedance-task-1"}}

    async def seedance_query(self, task_id):
        return {
            "code": 200,
            "data": {"status": "completed", "task_id": task_id, "video_url": "https://example.test/video.mp4"},
        }


class TaskRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_banana_sync_returns_image_url(self):
        from oai_bridge import tasks

        with patch.object(tasks, "OAIClient", return_value=FakeClient()):
            url = await tasks.run_app({"id": "banana", "mode": "banana_sync"}, {"prompt": "娴嬭瘯"})

        self.assertEqual(url, "https://example.test/image.png")

    async def test_general_async_polls_until_success(self):
        from oai_bridge import tasks

        with patch.object(tasks, "OAIClient", return_value=FakeClient()):
            with patch.object(tasks.asyncio, "sleep", return_value=None):
                url = await tasks.run_app({"id": "qwenedit", "mode": "task_submit"}, {"prompt": "娴嬭瘯"})

        self.assertEqual(url, "https://example.test/result.png")

    async def test_general_failed_task_includes_backend_detail(self):
        from oai_bridge import tasks
        from oai_bridge.client import OAIAPIError

        class FailedClient(FakeClient):
            async def query_task(self, task_id):
                return {
                    "code": 200,
                    "data": {"status": "failed", "task_id": task_id, "result": "图片尺寸过小"},
                }

        with patch.object(tasks, "OAIClient", return_value=FailedClient()):
            with self.assertRaises(OAIAPIError) as raised:
                await tasks.run_app({"id": "qwenedit", "mode": "task_submit"}, {"image": "https://example.test/a.png"})

        self.assertIn("图片尺寸过小", str(raised.exception))
    async def test_documented_workflow_apps_submit_and_poll_success(self):
        from oai_bridge import tasks

        documented_apps = [
            ({"id": "z-imagewenshengt", "mode": "task_submit", "label": "阿里造相-文生图"}, {"prompt": "测试", "num": 1, "magnification": 1.1, "aspect_ratio": "1:1", "use_pre_llm": False}),
            ({"id": "tupiankoutu", "mode": "task_submit", "label": "AI抠图"}, {"image": "https://example.test/a.png"}),
            ({"id": "kuotu", "mode": "task_submit", "label": "AI扩图"}, {"image": "https://example.test/a.png", "top": "1", "bottom": "1", "left": "1", "right": "1"}),
        ]

        for app, parameter in documented_apps:
            with self.subTest(app_id=app["id"]):
                with patch.object(tasks, "OAIClient", return_value=FakeClient()):
                    with patch.object(tasks.asyncio, "sleep", return_value=None):
                        url = await tasks.run_app(app, parameter)

                self.assertEqual(url, "https://example.test/result.png")

    async def test_general_image_tasks_timeout_after_fifteen_minutes(self):
        from oai_bridge import tasks
        from oai_bridge.client import OAIAPIError

        class PendingClient(FakeClient):
            async def query_task(self, task_id):
                self.polls += 1
                return {"code": 200, "data": {"status": "queued", "task_id": task_id, "result": ""}}

        client = PendingClient()
        monotonic_values = iter([0.0, 899.0, 901.0])
        with patch.object(tasks, "OAIClient", return_value=client):
            with patch.object(tasks.time, "monotonic", side_effect=lambda: next(monotonic_values)):
                with patch.object(tasks.asyncio, "sleep", return_value=None):
                    with self.assertRaises(OAIAPIError) as raised:
                        await tasks.run_app({"id": "z-imagewenshengt", "mode": "task_submit"}, {"prompt": "测试"})

        self.assertIn("任务轮询超时", str(raised.exception))
        self.assertEqual(client.polls, 1)

    async def test_seedance_video_tasks_timeout_after_thirty_minutes(self):
        from oai_bridge import tasks
        from oai_bridge.client import OAIAPIError

        class PendingSeedanceClient(FakeClient):
            async def seedance_query(self, task_id):
                self.polls += 1
                return {"code": 200, "data": {"status": "queued", "task_id": task_id}}

        client = PendingSeedanceClient()
        monotonic_values = iter([0.0, 1799.0, 1801.0])
        with patch.object(tasks, "OAIClient", return_value=client):
            with patch.object(tasks.time, "monotonic", side_effect=lambda: next(monotonic_values)):
                with patch.object(tasks.asyncio, "sleep", return_value=None):
                    with self.assertRaises(OAIAPIError) as raised:
                        await tasks.run_app({"id": "seedance", "mode": "seedance"}, {"prompt": "测试"})

        self.assertIn("Seedance 任务轮询超时", str(raised.exception))
        self.assertEqual(client.polls, 1)
    async def test_seedance_returns_video_url(self):
        from oai_bridge import tasks

        with patch.object(tasks, "OAIClient", return_value=FakeClient()):
            url = await tasks.run_app({"id": "seedance", "mode": "seedance"}, {"prompt": "娴嬭瘯"})

        self.assertEqual(url, "https://example.test/video.mp4")


if __name__ == "__main__":
    unittest.main()



