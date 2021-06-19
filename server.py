import os
import socket
import threading
import time
import pickle
'''
[Requirement] python3
[Requirement] gpustat: pip install gpustat --user
'''


class AllocateServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8885)
        print('Binding...')
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        print('Binding successful!')
        self.running_hist = []
        self.waiting_list = []
        self.reserve_num = 0

    '''
    arthur1  Wed Aug 22 15:29:01 2018
    [0] GeForce GTX 1080 Ti | 83'C,  55 % | 10911 / 11170 MB | yuhuiz(10901M)
    [1] GeForce GTX 1080 Ti | 84'C,  98 % | 10931 / 11172 MB | yuhuiz(10921M)
    [2] GeForce GTX 1080 Ti | 34'C,   0 % | 10734 / 11172 MB | amiratag(307M) amiratag(10417M)
    [3] GeForce GTX 1080 Ti | 29'C,   0 % | 10490 / 11172 MB | amiratag(213M) amiratag(10267M)
    '''

    def GetIdleId(self):
        idleid = []
        info = os.popen('gpustat').readlines()
        for line in info[1:]:
            splitline = line.split('|')
            usage = splitline[-1].strip()
            if len(usage) == 0:
                gpuid = int(splitline[0].split(' ')[0][1:-1])
                idleid.append(gpuid)
        return idleid

    def Execute(self):
        if len(self.waiting_list) == 0: return
        idleid = self.GetIdleId()
        if len(idleid) <= self.reserve_num: return
        command = self.waiting_list.pop(0)
        command.append(idleid[0])
        command.append(time.asctime())
        run = os.popen('CUDA_VISIBLE_DEVICES=%s %s' % (idleid[0], command[0]))
        self.running_hist.append(command)

    def AddWaitList(self, command):
        self.waiting_list.append([command, time.asctime()])

    def ShowWaitList(self):
        if len(self.waiting_list) == 0:
            print('Waiting list is empty')
        else:
            for i, command in enumerate(self.waiting_list):
                print('[%s](%s): %s' % (i, command[1], command[0]))

    def ShowRunHist(self):
        if len(self.running_hist) == 0:
            print('Running history is empty')
        else:
            for i, command in enumerate(self.running_hist):
                print('[%s]{GPU: %s}(%s->%s): %s' % (i, command[2], command[1], command[3], command[0]))

    def run(self):
        print('start')
        while True:
            print('running')
            connection, client_address = self.sock.accept()
            print('accepting')
            try:
                while True:
                    command = connection.recv(4096)
                    if command:
                        real_command = pickle.loads(command)
                        print(real_command)
                        if real_command[0]==4:
                            connection.close()
                            self.sock.close()
                            return 
                        connection.send(command)
                    else:
                        break
            finally:
                # Clean up the connection
                connection.close()
            # self.Execute()


if __name__ == '__main__':
    allocator = AllocateServer()
    allocator.start()
    allocator.join()
