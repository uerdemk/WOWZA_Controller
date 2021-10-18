import tkinter
import queue
from tkinter import *
import json
import requests
from requests.auth import HTTPDigestAuth
import time
import threading
import os

starting = 0  #başlangıç durumu kontrol için kullanılmaktadır.

desired_run_condition = "mini"
#desired_run_condition = "full"

username = "admin"
password = "admin"

cluster_ip = "127.0.0.1"
#cluster_ip = "localhost"

headers = {
    "Accept":"application/json",
    "Content-Type":"application/json",
    "charset":"utf-8"
}

record_payload = {"instanceName": "_definst_",
                   "fileVersionDelegateName": "",
                   "serverName": "",
                   "recorderName": "",
                   "currentSize": 0,
                   "segmentSchedule": "",
                   "startOnKeyFrame": True,
                   "outputPath": "",
                   "currentFile": "",
                   "saveFieldList": [
                       ""
                   ],
                   "recordData": False,
                   "applicationName": "",
                   "moveFirstVideoFrameToZero": False,
                   "recorderErrorString": "",
                   "segmentSize": 0,
                   "defaultRecorder": False,
                   "splitOnTcDiscontinuity": False,
                   "version": "",
                   "baseFile": "",
                   "segmentDuration": 0,
                   "recordingStartTime": "",
                   "fileTemplate": "",
                   "backBufferTime": 0,
                   "segmentationType": "",
                   "currentDuration": 0,
                   "fileFormat": "",
                   "recorderState": "",
                   "option": ""
                   }

stream_payload = {
   "name": "",
   "serverName": "_defaultServer_",
   "uri": ""
}


url_get_stream = 'http://' + cluster_ip + ':8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/streamfiles'
url_get_record = 'http://' + cluster_ip + ':8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/instances/_definst_/streamrecorders'
print(url_get_stream)
print(url_get_record)
if os.path.exists("WoW_log.txt"):
    os.remove("WoW_log.txt")

recording_list = [""]
break_val = 0

with open("Stream.txt", "r") as stream:
    stream_name = stream.read().split()

stream_list = stream_name
record = [""] * len(stream_list)
for z in range(len(stream_list)):
    record[z] = stream_list[z] + ".stream"
record.sort()

with open("Address.txt", "r") as address:
    address_name = address.read().split()

def logging(log_text):
    time_info = time.asctime(time.localtime(time.time()))
    with open("WoW_log.txt", "a+") as file_log:
        file_log.write(time_info + "  ->  " + "  ->  " + log_text + "\n")

print("---------------------------------%Starting%-----------------------------------------------")
#logging("---------------------------------%Starting%-----------------------------------------------")

print("stream_list=     ", stream_list)
#logging("stream_list=" + str(stream_list))
print("record           ", record)
#logging("record=" + str(record))

stream_uri = address_name
print("stream_uri=      ", stream_uri)
#logging("stream_uri=" + str(stream_uri))
url_stream = []

color_stream = ["red"] * len(stream_list)
#color_record = ["red"] * len(stream_list)
addStream = [Button] * len(stream_list)
#addRecord = [Button] * len(stream_list)


class StreamPart:
    def __init__(self):
        self.s = requests.get(url_get_stream, auth=HTTPDigestAuth(username, password), headers=headers, timeout=10)
        self.s_json = self.s.json()
        self.r = requests.get(url_get_record, auth=HTTPDigestAuth(username, password), headers=headers, timeout=10)
        self.r_json = self.r.json()
        #print(json.dumps(self.r_json, indent=2))
        print(self.s.status_code)
        print(self.r.status_code)
        #print(json.dumps(self.r_json, indent=4))

    def check_streaming(self):
        global root
        global frame_1
        global frame_2
        global color_stream
        #global color_record
        global stream
        #global s_json
        global stream_payload
        global record_payload
        stream_OK = []
        try:
            #for y in range(len(stream_list)):
            yt = len(self.s_json["streamFiles"])
            yt_value = yt
            if yt == 0:
                 yt_value = len(stream_list)
            for y in range(yt_value):
                for z in range(len(stream_list)):
                    stream_payload["name"] = stream_list[z]
                    stream_payload["uri"] = stream_uri[z]
                    if self.s_json["streamFiles"][y]["id"] == stream_list[z]:
                        print("\"{stream_name}.stream\" is OK".format(stream_name=stream_list[z]))
                        #logging("\"{stream_name}.stream\" is OK".format(stream_name=stream_list[z]))
                        self.connect_stream(stream_list[z], z)
                        stream_OK.append(stream_list[z])
                        #print("stream_OK=", stream_OK)
                    try:
                        aaa = stream_OK.index(stream_list[z])
                        #print("aaa=", aaa)
                    except:
                        aaa = ""
                        #print("aaa=", aaa)

                    if self.s_json["streamFiles"][y]["id"] != stream_list[z] and aaa == "":
                        #print("Streaming has just stopped for", "\"", stream_list[z], ".stream", "\""". Trying to start streaming again...")
                        #print("stream_payload=", stream_payload)
                        s = requests.post(url_get_stream, auth=HTTPDigestAuth(username, password), data=json.dumps(stream_payload),
                                          headers=headers, timeout=10)
                        self.connect_stream(stream_list[z], z)
            self.tkinter_GUI()

        except:
            for y in range(len(stream_list)):
                stream_payload["name"] = stream_list[y]
                stream_payload["uri"] = stream_uri[y]
                print("Stream has just stopped for", "\"", stream_list[y], ".stream", "\""". Trying to start streaming again...(except)")
                print("url_get_stream= ", url_get_stream)
                print("stream_payload=", stream_payload)
                s = requests.post(url_get_stream, auth=HTTPDigestAuth(username, password), data=json.dumps(stream_payload),
                                  headers=headers, timeout=10)
                print(s)
                print("Code:", s.status_code)
                if s.status_code == 200:
                    print("Stream created...(except)")
                    self.connect_stream(self, stream_list[z], z)
                else:
                    print("problem...(except)")
                    color_stream[y] = "red"
                self.tkinter_GUI()
        return

    def connect_stream(self, stream_list_val, val_index):
        global stream
        global stream_payload
        global record_payload
        global color_stream
        #global color_record
        try:
            uri_connect = "http://" + cluster_ip + ":8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/streamfiles/"+ str(stream_list_val) + "/actions/connect?connectAppName=live&appInstance=_definst_&mediaCasterType=rtp"
            #print("Connect for", "\"", stream_list_val, ".stream")
            #print("uri_connect=", uri_connect)
            c = requests.put(uri_connect, auth=HTTPDigestAuth(username, password), headers=headers, timeout=10)
            #print("Code:", c.status_code)
            if c.status_code == 200:
                #print("Stream created for {stream_list_val_val}".format(stream_list_val_val=stream_list_val))
                color_stream[val_index] = "yellow"
            else:
                print("problem")
                #logging("problem")
                color_stream[val_index] = "red"
            #self.tkinter_GUI()

        except:
            uri_connect = "http://" + cluster_ip + ":8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/streamfiles/" + str(
                stream_list[y]) + "/actions/connect?connectAppName=live&appInstance=_definst_&mediaCasterType=rtp"
            #print ("Connect for", "\"", stream_list_val, ".stream")
            c = requests.put(uri_connect, auth=HTTPDigestAuth(username, password), headers=headers, timeout=10)
            #print("Code:", c.status_code)
            if c.status_code == 200:
                print("Stream created...")
            else:
                print("problem")
            self.tkinter_GUI(self)
        return

    def tkinter_GUI(self):
        global th_timer
        global root
        global frame_1
        global frame_2
        global color_stream
        #global color_record
        global stream_list
        #global s_json
        global stream_payload
        global record_payload
        #global addRecord
        global addStream
        #print("color_stream=", color_stream, "color_record=", color_record)
        try:
            for z in range(len(stream_list)):
                addStream[z].configure(bg=color_stream[z], command=threading.Thread().start())
                #addRecord[z].configure(bg=color_record[z], command=threading.Thread().start())
                #print("color_stream[{z_value}]=".format(z_value=z), color_stream[z])
                #print("color_record[{z_value}]=".format(z_value=z), color_record[z])
        except:
            ...
        return

    def check_recording(self):
        global root
        global frame_1
        global frame_2
        global color_stream
        #global color_record
        global url_stream
        global record
        #global r_json
        global stream_payload
        global record_payload
        global break_val

        try:
            recording_list = [""] * len(self.r_json["streamrecorder"])
            for it in range(len(self.r_json["streamrecorder"])):
                recording_list[it] = self.r_json["streamrecorder"][it]["recorderName"]
        except:
            recording_list = []

        recording_list.sort()
        print(recording_list)

        deletions = [x for x in record if x not in recording_list]
        deletions.sort()

        existing = [x for x in record if x not in deletions]
        existing.sort()

        try:
            # print(len(r_json["streamrecorder"]))
            record_waiting = []
            for y in range(len(self.r_json["streamrecorder"])):
                if self.r_json["streamrecorder"][y]["recorderState"] != "Recording in Progress":
                    # print(r_json["streamrecorder"][y]["recorderName"])
                    record_waiting.append(self.r_json["streamrecorder"][y]["recorderName"])
        except:
            print("...")

        existing_and_recorded = [x for x in existing if x not in record_waiting]
        existing_and_recorded.sort()

        # print("record=              ", record)
        # print("recording_list=      ", recording_list)
        print("deletions=                       ", deletions)
        #logging("deletions=" + str(deletions))
        print("record_waiting=                  ", record_waiting)
        #logging("record_waiting=" + str(record_waiting))
        print("existing=                        ", existing)
        #logging("existing=" + str(existing))
        print("existing_and_recorded=           ", existing_and_recorded)
        #logging("existing_and_recorded=" + str(existing_and_recorded))

        for z in range(len(deletions)):
            print("----------------Deletions----------------------------")
            record_payload["recorderName"] = deletions[z]
            url_start_record = 'http://' + cluster_ip + ':8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/instances/_definst_/streamrecorders/' + str(
                deletions[z])
            r = requests.post(url_start_record, auth=HTTPDigestAuth(username, password),
                              data=json.dumps(record_payload),
                              headers=headers, timeout=10)
            print("Code:", r.status_code, "recorderName=", deletions[z], url_start_record)
            #logging("Code:" + str(r.status_code) + "recorderName=" + str(deletions[z]) + str(url_start_record))

        #for i in range(len(record)):
        #    color_record[i] = "red"
        for i in record:
            for k in existing_and_recorded:
                if i == k:
                    #color_record[record.index(i)] = "green"
                    color_stream[record.index(i)] = "green"
                else:
                    ...
            for b in record_waiting:
                if i == b:
                    #color_record[record.index(i)] = "yellow"
                    color_stream[record.index(i)] = "blue"
                else:
                    ...
        # print("color_record=", color_record)
        self.tkinter_GUI()
        return

    def check_recording_mini(self):
        global root
        global frame_1
        global frame_2
        global color_stream
        #global color_record
        global url_stream
        global record
        #global r_json
        global stream_payload
        global record_payload
        global break_val

        try:
            recording_list = [""] * len(self.r_json["streamrecorder"])
            for it in range(len(self.r_json["streamrecorder"])):
                recording_list[it] = self.r_json["streamrecorder"][it]["recorderName"]
        except:
            recording_list = []

        recording_list.sort()
        #print(recording_list)

        deletions = [x for x in record if x not in recording_list]
        deletions.sort()

        existing = [x for x in record if x not in deletions]
        existing.sort()

        try:
            # print(len(r_json["streamrecorder"]))
            record_waiting = []
            for y in range(len(self.r_json["streamrecorder"])):
                if self.r_json["streamrecorder"][y]["recorderState"] != "Recording in Progress":
                    # print(r_json["streamrecorder"][y]["recorderName"])
                    record_waiting.append(self.r_json["streamrecorder"][y]["recorderName"])
        except:
            print("...")

        existing_and_recorded = [x for x in existing if x not in record_waiting]
        existing_and_recorded.sort()

        # print("record=              ", record)
        # print("recording_list=      ", recording_list)
        print("deletions=                       ", deletions)
        #logging("deletions=" + str(deletions))
        print("record_waiting=                  ", record_waiting)
        #logging("record_waiting=" + str(record_waiting))
        print("existing=                        ", existing)
        #logging("existing=" + str(existing))
        print("existing_and_recorded=           ", existing_and_recorded)
        #logging("existing_and_recorded=" + str(existing_and_recorded))

        #for i in range(len(record)):
        #    color_record[i] = "red"
        for i in record:
            for k in existing_and_recorded:
                if i == k:
                    #color_record[record.index(i)] = "green"
                    color_stream[record.index(i)] = "green"
                else:
                    ...
            for b in record_waiting:
                if i == b:
                    #color_record[record.index(i)] = "yellow"
                    color_stream[record.index(i)] = "blue"
                else:
                    ...
            for kb in deletions:
                if i == kb:
                    #color_record[record.index(i)] = "green"
                    color_stream[record.index(i)] = "red"
                else:
                    ...
        # print("color_record=", color_record)
        self.tkinter_GUI()
        return


class GuiPart:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        if desired_run_condition == "full":
            frame_1 = LabelFrame(root, text="Red= Not Connected, Yellow= Just Connected, Blue= Connected and Waiting, Green= Recording", width=100, height=1, padx=1, pady=1,
                                 command=threading.Thread().start())
            frame_1.grid(row=0, column=0, columnspan=3)
        if desired_run_condition == "mini":
            frame_1 = LabelFrame(root, text="Red= Not Connected, Blue= Connected and Waiting, Green= Recording", width=100, height=1, padx=1, pady=1,
                                 command=threading.Thread().start())
            frame_1.grid(row=0, column=0, columnspan=3)
        #frame_2 = LabelFrame(root, text="Record-> Green = Recording, Red = Not Recording, Yellow = Waiting for Stream", width=100, height=1, padx=1, pady=1,
        #                     command=threading.Thread().start())
        #frame_2.grid(row=1, column=0, columnspan=3)
        for z in range(len(stream_list)):
            addStream[z] = Button(frame_1, bg=color_stream[z], text=stream_list[z], padx=40, pady=20, width=15, height=1,
                                  command=threading.Thread().start())
            addStream[z].grid(row=0, column=0 + z)
            #addRecord[z] = Button(frame_2, bg=color_record[z], text=stream_list[z], padx=40, pady=20, width=10, height=1,
            #                      command=threading.Thread().start())
            #addRecord[z].grid(row=0, column=0 + z)
        # Add more GUI stuff here depending on your specific needs

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                #print(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue(  )

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall(  )

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        #self.gui.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        global starting
        while self.running:
            S1 = StreamPart()
            if desired_run_condition =="full":
                if starting < 2:
                    S1.check_streaming()
                else:
                    if starting - 10 == 0:
                        starting = 0
                starting += 1
                S1.check_recording()
            if desired_run_condition == "mini":
                S1.check_recording_mini()


    def endApplication(self):
        self.running = 0

#rand = random.Random(  )
root = tkinter.Tk(  )

client = ThreadedClient(root)
root.mainloop(  )