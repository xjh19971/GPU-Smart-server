import os
import socket
import threading
import time
import pickle
import logging
'''
[Requirement] python3
[Requirement] gpustat: pip install gpustat --user
'''
logging.basicConfig(filename='example.log', level=logging.DEBUG)

class AllocateServerExecuter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_flag = False
        self.pending_execute = []
        self.running_hist = []
        self.waiting_list = []

    def Execute(self):
        if len(self.waiting_list) == 0: return
        idleid = self.GetIdleId()
        if len(idleid) <= 0: return
        command = self.waiting_list.pop(0)
        command.append(idleid[0])
        command.append(time.asctime())
        run = os.popen('CUDA_VISIBLE_DEVICES=%s %s' % (idleid[0], command[0]))
        self.running_hist.append(command)

    def run(self):
        while self.stop_flag is not True:
            self.Execute()
            time.sleep(5)

class AllocateServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8885)
        logging.info('Binding...')
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        logging.info('Binding successful!')
        self.running_hist = []
        self.waiting_list = []
        self.executor = AllocateServerExecuter()
        self.executor.start()

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


    def AddWaitList(self, command):
        self.waiting_list.append([command, time.asctime()])

    def UpdateFromExecutor(self):
        self.waiting_list = self.executor.waiting_list
        self.running_hist = self.executor.running_hist

    def ShowWaitList(self):
        return_msg = ''
        if len(self.waiting_list) == 0:
            return_msg += 'Waiting list is empty\n'
        else:
            for i, command in enumerate(self.waiting_list):
                return_msg += '[%s](%s): %s\n' % (i, command[1], command[0])
        return return_msg

    def ShowRunHist(self):
        return_msg = ''
        if len(self.running_hist) == 0:
            return_msg+='Running history is empty\n'
        else:
            for i, command in enumerate(self.running_hist):
                return_msg+='[%s]{GPU: %s}(%s->%s): %s\n' % (i, command[2], command[1], command[3], command[0])
        return return_msg

    def run(self):
        logging.info('start')
        while True:
            logging.info('running')
            connection, client_address = self.sock.accept()
            logging.info('accepting')
            try:
                while True:
                    command = connection.recv(4096)
                    if command:
                        real_command = pickle.loads(command)
                        logging.debug(str(real_command))
                        if real_command[0] == 1:
                            return_msg = 'Command Added. Wait at most 5 secs to execute.'
                            self.AddWaitList(real_command[1])
                        if real_command[0] == 2:
                            return_msg = self.ShowRunHist()
                        if real_command[0] == 3:
                            return_msg = self.ShowWaitList()
                        if real_command[0] == 4:
                            connection.close()
                            self.sock.close()
                            self.executor.stop_flag = True
                            self.executor.join()
                            return
                        real_return_msg = pickle.dumps(return_msg)
                        connection.send(real_return_msg)
                    else:
                        break
            finally:
                # Clean up the connection
                connection.close()
            self.Execute()


if __name__ == '__main__':
    allocator = AllocateServer()
    allocator.start()
    allocator.join()
