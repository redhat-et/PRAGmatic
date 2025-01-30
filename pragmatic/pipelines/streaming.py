from threading import Thread, Event
from queue import Queue

class RagStreamHandler:
    def __init__(self, settings):
        self._timeout = settings.get("streaming_timeout", 60)  # seconds
        self._stream_queue = None
        self._stream_thread = None
        self._stop_event = Event()

    def __del__(self):
        """
        Finalizer for cleanup. Ensures threads and resources are released.
        """
        self.stop_stream()

    def _streaming_callback(self, chunk):
        """
        Callback to be passed to the LLM, which places streamed tokens into the queue.
        """
        if self._stream_queue:
            self._stream_queue.put(chunk.content)

    def _run_streaming_in_thread(self, run_callable):
        """
        Invokes the provided callable (the pipeline's run method),
        then signals the end of streaming by putting None in the queue.
        """
        run_callable()
        if self._stream_queue:
            self._stream_queue.put(None)

    def start_stream(self, run_callable):
        """
        Initializes the queue and the background thread that executes `run_callable`.
        """
        self._stream_queue = Queue()
        self._stream_thread = Thread(target=self._run_streaming_in_thread, args=(run_callable,))
        self._stream_thread.start()

    def stop_stream(self):
        """
        Gracefully stops the streaming thread if it is running.
        """
        if self._stream_thread and self._stream_thread.is_alive():
            self._stop_event.set()  # Signal the thread to stop
            self._stream_thread.join()  # Wait for the thread to finish
        self._stream_queue = None  # Clean up the queue
        self._stop_event.clear()  # Reset the flag for future use

    def stream_chunks(self):
        """
        Yields streamed chunks from the queue. 
        Terminates when `None` is retrieved from the queue.
        """
        try:
            for chunk in iter(lambda: self._stream_queue.get(timeout=self._timeout), None):
                yield chunk
        finally:
            self.stop_stream()
