# -*- coding: utf-8 -*-
"""spine 的哈希链能抓到什么、抓不到什么。

test_manifest.py 那份跑的是 D:\eda 上的真产物，只能在这台机器上跑。这里
的每一条都自己造一个小 flow，所以它在哪里都能跑——这也是它被放进 CI 的
理由。每一条对应用户能说出口的一句怀疑。
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "agentic"))

from spine import Flow, Stage, verify_manifest


def _emit(inp, wd):
    f = os.path.join(wd, "a.txt")
    with open(f, "w", encoding="utf-8") as fh:
        fh.write("hello")
    return {"a": f}


def _extend(inp, wd):
    f = os.path.join(wd, "b.txt")
    with open(inp["a"], encoding="utf-8") as src, \
            open(f, "w", encoding="utf-8") as dst:
        dst.write(src.read() + " world")
    return {"b": f}


def _build():
    root = tempfile.mkdtemp(prefix="spine-test-")
    fl = Flow(root)
    fl.run(Stage("one", _emit, (), ("a",), tool="python"))
    fl.run(Stage("two", _extend, ("a",), ("b",), tool="python"))
    return fl, fl.save()


class TestChain(unittest.TestCase):

    def test_a_fresh_manifest_verifies(self):
        _, mp = _build()
        self.assertEqual(verify_manifest(mp), (True, []))

    def test_an_artifact_changed_on_disk_is_caught(self):
        """产物被改了一个字节，manifest 必须报出来。

        这是 manifest 存在的唯一理由：同样的流水线跑两遍都同意，那只说明
        它确定，不说明它对。第三方改了产物还能验过，就等于没验。
        """
        fl, mp = _build()
        with open(fl.artifacts["b"], "a", encoding="utf-8") as fh:
            fh.write("!")
        ok, problems = verify_manifest(mp)
        self.assertFalse(ok)
        self.assertTrue(any("artifact changed on disk" in p for p in problems), problems)

    def test_an_edited_record_is_caught(self):
        """把某一段的 ok 从真改成假，链必须断。"""
        _, mp = _build()
        m = json.load(open(mp, encoding="utf-8"))
        m["stages"][1]["ok"] = False
        json.dump(m, open(mp, "w", encoding="utf-8"))
        ok, problems = verify_manifest(mp, check_files=False)
        self.assertFalse(ok)
        self.assertTrue(any("chain break" in p for p in problems), problems)

    def test_a_repointed_artifact_is_caught(self):
        """路径和字节数也在链上，不只是 sha256。

        原来链只覆盖 sha256，于是把某个产物指向别的路径、换个字节数，
        整份 manifest 照样验过（实测 (True, [])）。一份能被随手改指向的
        记录不是证据。
        """
        _, mp = _build()
        m = json.load(open(mp, encoding="utf-8"))
        m["stages"][1]["hashes"]["b"]["bytes"] = 999999
        m["stages"][1]["hashes"]["b"]["path"] = "/somewhere/else.txt"
        json.dump(m, open(mp, "w", encoding="utf-8"))
        ok, problems = verify_manifest(mp, check_files=False)
        self.assertFalse(ok)
        self.assertTrue(any("chain break" in p for p in problems), problems)

    def test_a_truncated_tail_is_caught(self):
        """砍掉最后一段，head 对不上。"""
        _, mp = _build()
        m = json.load(open(mp, encoding="utf-8"))
        m["stages"] = m["stages"][:-1]
        json.dump(m, open(mp, "w", encoding="utf-8"))
        ok, problems = verify_manifest(mp, check_files=False)
        self.assertFalse(ok)
        self.assertTrue(any("head mismatch" in p for p in problems), problems)

    def test_a_declared_output_that_was_not_produced_fails_the_stage(self):
        """声明了输出却没产出，这一段就是失败的。

        不能让"没产出"和"产出了空文件"看起来一样。
        """
        def lazy(inp, wd):
            return {}
        root = tempfile.mkdtemp(prefix="spine-test-")
        fl = Flow(root)
        r = fl.run(Stage("lazy", lazy, (), ("a",), tool="python"))
        self.assertFalse(r.ok)
        self.assertIn("not produced", r.error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
