import multiprocessing
import asyncio

asyncio.open_connection(
    
)


def producer(queue):
    for i in range(5):
        queue.put(i)

def consumer(queue):
    while not queue.empty():
        item = queue.get()
        print(f'Item: {item}')

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer, args=(queue,))
    p2 = multiprocessing.Process(target=consumer, args=(queue,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()