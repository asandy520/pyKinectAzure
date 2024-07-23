import subprocess
import signal
import time
import os
import SkeletonTracker
import threading

# array_prepare_for_picoscenes 3 "5640 160 5250"
class Exec_Cmd():
    def __init__(self) -> None:
        self.process = subprocess.Popen('echo "Ready to execute command!"', shell=True)
        self.orbbec_processor = SkeletonTracker.SkeletonTracker()
        self.pipeline_started = False

    def run(self, cmd: str):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout.decode('utf-8').split('\n')
        stderr = stderr.decode('utf-8').split('\n')
        return stdout, stderr
    
    def exec(self, cmd: str):
        cmd = cmd.split(' ')
        if cmd[0] == 'stdby':
            # self.orbbec.configure_pipeline()
            print("Femto Bolt camera in standby mode!!!!!!!!")
            timestring = time.strftime("%y%m%d_%H%M%S", time.localtime())
            return timestring
        
        elif cmd[0] == 'start':
            print('Start Event')
            if not self.orbbec_processor.event.is_set():
                folder_path = cmd[2]
                self.run(f'mkdir -p {folder_path}')
                self.thread = threading.Thread(target=self.orbbec_processor.track_skeleton, args=(folder_path,))
                self.thread.start()
            else:
                print('Already started.')
                
        elif cmd[0] == 'stop':
            if self.orbbec_processor.event.is_set():
                print("Femto Bolt Camera already stopped.")
            else:
                self.orbbec_processor.stop_tracking()
                print("Femto Bolt Camera stopped.")

        elif cmd[0] == 'beep' and cmd[1] == '1':
            self.run('beep -f 2000 -r 1 -d 100 -l 50')
        
        elif cmd[0] == 'beep' and cmd[1] == '2':
            self.run('beep -f 2000 -r 2 -d 100 -l 50')