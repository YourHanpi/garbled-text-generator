# -*- coding: utf-8 -*-
from pynput.keyboard import Controller, GlobalHotKeys, Key
import pyperclip

import random

from hashlib import md5
import time
from typing import Callable


class ClipboardRecover:

    def __init__(self):
        self._clipboard_data: str = ""

    def recover(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            self._clipboard_data = pyperclip.paste()
            result = func(*args, **kwargs)
            pyperclip.copy(self._clipboard_data)
            return result
        return wrapper


clipboard_recover = ClipboardRecover()


class GarbledTextGenerator:

    def __init__(self):
        self._key_controller = Controller()
        self._hotkeys: dict[str, Callable] = {}
        self._mode: int = 0
        self._generators: list[Callable[[int], str]] = [self._generate_cjk_text, self._generate_ascii_text]
        self._mode_names: list[str] = ["中日韩文字", "ASCII"]
        self._set_hotkeys()

    @clipboard_recover.recover
    def paste_texts(self) -> None:
        self._key_controller.press(Key.ctrl)
        self._key_controller.tap("a")
        self._key_controller.tap("x")
        self._key_controller.release(Key.ctrl)
        time.sleep(0.05)
        inputs: str = pyperclip.paste()
        inputs = inputs[:-1] if inputs.endswith("g") else inputs
        seed = md5(inputs.encode("utf-8")).hexdigest()
        random.seed(seed)
        generating_length = len(inputs)
        text: str = self._generators[self._mode](generating_length)
        self._key_controller.release("\x07")
        self._key_controller.release(Key.ctrl)
        self._key_controller.type(text)
        print(f"已生成乱码。种子：{seed}；长度：{generating_length}。")

    def print_current_mode(self) -> None:
        print(f"当前输出模式: {self._mode_names[self._mode]}")

    def print_manual(self) -> None:
        modes_manual: str = "\n".join([f"{i + 1}.按下Ctrl+{i + 1}：切换为{self._mode_names[i]}" for i in range(len(self._mode_names))])
        print(f"""本程序由 白霜渡鸦_Corvus 开发，按照GNU GPLv3协议发布。
本程序使用Python 3.12开发，依赖的第三方库有pynput和pyperclip。

---程序使用方法---
1.在任意窗口输入文字之后，按下Ctrl+G即可根据当前文字生成等长度的乱码。如果未选中文字，则会根据剪贴板中的文字生成乱码。\u001b[31m警告：原有文字会被覆盖，但剪贴板不会被覆盖。\u001b[0m
2.按下Ctrl+H获取帮助。
3.按下Ctrl+0查看当前输出模式。
4.按下Esc退出程序。

---输出模式切换方法---
{modes_manual}
""")

    def set_mode(self, mode: int) -> None:
        self._mode = mode
        print(f"已切换输出模式为: {self._mode_names[self._mode]}")

    def start_listening(self) -> None:
        hotkeys = GlobalHotKeys(self._hotkeys)
        hotkeys.start()
        hotkeys.join()

    def _set_hotkeys(self) -> None:
        self._hotkeys.update({
            "<ctrl>+1": lambda: self.set_mode(0),
            "<ctrl>+2": lambda: self.set_mode(1),
            "<esc>": lambda: exit(0),
            "<ctrl>+0": self.print_current_mode,
            "<ctrl>+h": self.print_manual,
            "<ctrl>+g": self.paste_texts
        })

    @staticmethod
    def _generate_ascii_text(length: int) -> str:
        return "".join([chr(random.randint(0x20, 0x7E)) for _ in range(length)])

    @staticmethod
    def _generate_cjk_text(length: int) -> str:
        return "".join([chr(random.randint(0x4E00, 0x9FA5)) for _ in range(length)])


def main() -> None:
    garbled_text_generator = GarbledTextGenerator()
    garbled_text_generator.print_manual()
    garbled_text_generator.start_listening()


if __name__ == "__main__":
    main()
