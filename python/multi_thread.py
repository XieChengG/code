import threading
import time


class WorkerThread(threading.Thread):
    def __init__(self, thread_id, name, delay):
        super(WorkerThread, self).__init__()
        self.thread_id = thread_id
        self.name = name
        self.delay = delay

    def run(self):
        print(f"开始线程: {self.name}")
        print_work(self.name, self.delay, 5)
        print(f"退出线程: {self.name}")


def print_work(thread_name, delay, counter):
    while counter:
        time.sleep(delay)
        print(f"{thread_name}: {time.ctime(time.time())} (计数: {counter})")
        counter -= 1


if __name__ == "__main__":
    thread1 = WorkerThread(1, "线程-1", 1)
    thread2 = WorkerThread(2, "线程-2", 1.5)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
