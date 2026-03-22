import asyncio
import inspect
import signal
import threading
from collections.abc import Awaitable, Callable

from core.logging import logger


CleanupHook = Callable[[], Awaitable[None] | None]


class GracefulShutdownController:
    def __init__(self):
        self._shutdown_event = threading.Event()
        self._shutdown_lock = threading.Lock()
        self._cleanup_hooks: list[tuple[str, CleanupHook]] = []
        self._signal_handlers_installed = False
        self._previous_handlers: dict[int, object] = {}

    def install_signal_handlers(self):
        if self._signal_handlers_installed:
            return

        signals_to_handle = [signal.SIGINT, signal.SIGTERM]

        if hasattr(signal, "SIGBREAK"):
            signals_to_handle.append(signal.SIGBREAK)

        any_installed = False

        for sig in signals_to_handle:
            try:
                self._previous_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, self._make_signal_handler(sig))
                any_installed = True
            except (OSError, RuntimeError, ValueError):
                logger.warning(f"Unable to register signal handler for {sig}")

        self._signal_handlers_installed = any_installed

    def _make_signal_handler(self, sig: int):
        def _handler(_signum, _frame):
            self.request_shutdown(f"signal:{sig}")

            previous = self._previous_handlers.get(sig)

            if callable(previous):
                previous(_signum, _frame)
            elif previous == signal.SIG_DFL and sig == signal.SIGINT:
                raise KeyboardInterrupt

        return _handler

    def request_shutdown(self, reason: str = "unknown"):
        with self._shutdown_lock:
            if self._shutdown_event.is_set():
                return

            logger.info(f"Shutdown requested ({reason})")
            self._shutdown_event.set()

    def is_shutdown_requested(self) -> bool:
        return self._shutdown_event.is_set()

    async def wait_for_shutdown(self, poll_interval: float = 0.2):
        while not self._shutdown_event.is_set():
            await asyncio.sleep(poll_interval)

    def clear(self):
        self._shutdown_event.clear()

    def register_cleanup_hook(self, name: str, hook: CleanupHook):
        self._cleanup_hooks.append((name, hook))

    async def run_cleanup_hooks(self):
        for name, hook in self._cleanup_hooks:
            try:
                result = hook()
                if inspect.isawaitable(result):
                    await result
                logger.info(f"Cleanup hook completed: {name}")
            except Exception as exc:
                logger.error(f"Cleanup hook failed ({name}): {exc}")


shutdown_manager = GracefulShutdownController()
