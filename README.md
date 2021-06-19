# GPU-Smart-server: Server version for Interactive Automatic GPU Manager
Inspired by GPU-Smart(https://github.com/yuhui-zh15/GPU-Smart), I create a server-client version to run the controller at background.   

Note: Currently, reserve_num in original repo is disabled. The time in running history only shows the waiting time instread of waiting time + running time 
## Version 0.1

### Usage

Run `./start_server.sh` to start server

Run `python client.py` 

### Requirements

gpustat==0.4.1


### New Command
```
Please input command
<Your Command Here>
If you want to run with conda, always run a bash script with 'conda activate ...'.
```


