import os
import pickle
import socket
import threading

'''
[Requirement] python3
[Requirement] gpustat: pip install gpustat --user
'''


class AllocateClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8880)
        self.sock.connect(self.server_address)
        print('Welcome to Smart GPU Queue')
        print('--------------------------')
        print('[1] New Command')
        print('[2] Running History')
        print('[3] Waiting List')
        print('[4] GPU Status')
        print('[h] Help')
        print('[k] Kill server and exit')
        print('[q] Exit')
        print('--------------------------')

    def get_command(self):
        msg = None
        cid = input('Please input command ID\n')
        if cid == '1':
            command = input('Please input command\n')
            msg = [1, command]
            # allocator.AddWaitList(command)
        elif cid == '2':
            msg = [2, None]
            # allocator.ShowRunHist()
        elif cid == '3':
            msg = [3, None]
            # allocator.ShowWaitList()
        elif cid == '4':
            os.system('gpustat')
        elif cid == '':
            pass
        elif cid == 'q':
            return 1
        elif cid == 'k':
            msg = [4, None]
        elif cid == 'h':
            print('Welcome to Smart GPU Queue')
            print('--------------------------')
            print('[1] New Command')
            print('[2] Running History')
            print('[3] Waiting List')
            print('[4] GPU Status')
            print('[h] Help')
            print('[q] Exit')
            print('--------------------------')
            pass
        else:
            print('Error command!')
        if msg != None:
            real_msg = pickle.dumps(msg)
            self.sock.sendall(real_msg)
            real_response = self.sock.recv(0)
            response = pickle.loads(real_response)
            print(str(response))
            if msg == [4, None]:
                return 1
        return 0

    def run(self):
        while self.get_command() != 1:
            pass


if __name__ == '__main__':
    client = AllocateClient()
    client.start()
    client.join()
