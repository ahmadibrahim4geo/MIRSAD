"""QProcess boundary keeps native GIS failures out of the main application."""
import json
import sys
import uuid
from pathlib import Path
from PySide6.QtCore import QObject,QProcess,QProcessEnvironment,QTimer,Signal
from .jobs import clean
from .validation import bounded_json

class ProcessWorker(QObject):
    progress=Signal(object)
    finished=Signal(object)
    failed=Signal(str)
    stopped=Signal()
    def __init__(self,request,folder,parent=None):
        super().__init__(parent)
        request=dict(request)
        credentials=request.pop("_credentials",None)
        self.secret_payload=(json.dumps(credentials,ensure_ascii=True)+"\n").encode("utf-8") if credentials else b""
        if len(self.secret_payload)>32768:raise ValueError("Credentials exceed the supported size")
        if credentials:request["requires_credentials"]=True
        self.directory=Path(folder).resolve()/".mirsad-jobs"/uuid.uuid4().hex
        self.directory.mkdir(parents=True,exist_ok=False)
        self.path=self.directory/"request.json"
        self.path.write_text(json.dumps(clean(request),ensure_ascii=False,allow_nan=False),encoding="utf-8")
        if self.path.stat().st_size>256*1024*1024:raise ValueError("Job request is too large.")
        self.process=QProcess(self);self.buffer=b"";self.stderr="";self.error="";self.cancel_requested=False;self.done=False
        self.process.started.connect(self.send_credentials)
        environment=QProcessEnvironment.systemEnvironment();environment.insert("PYTHONIOENCODING","utf-8")
        environment.insert("MPLBACKEND","Agg");self.process.setProcessEnvironment(environment)
        environment.insert("MIRSAD_JOB_ID",self.directory.name);self.process.setProcessEnvironment(environment)
        self.process.readyReadStandardOutput.connect(self.read_stdout);self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.exited);self.process.errorOccurred.connect(self.process_error)
        self.kill_timer=QTimer(self);self.kill_timer.setSingleShot(True);self.kill_timer.setInterval(75000)
        self.kill_timer.timeout.connect(self.process.kill)
    def start(self):
        if getattr(sys,"frozen",False):command,args=sys.executable,["--run-job",str(self.path)]
        else:command,args=sys.executable,["-I",str(Path(__file__).resolve().parents[2]/"launcher.py"),"--run-job",str(self.path)]
        self.process.setWorkingDirectory(str(self.directory));self.process.start(command,args)
    def send_credentials(self):
        if self.secret_payload:self.process.write(self.secret_payload)
        self.secret_payload=b"";self.process.closeWriteChannel()
    def cancel(self):
        if self.cancel_requested:return
        self.cancel_requested=True;(self.directory/"cancel").touch();self.kill_timer.start()
        self.progress.emit("Cancellation requested. An unresponsive worker will be stopped after 75 seconds.")
    def read_stdout(self):
        self.buffer+=bytes(self.process.readAllStandardOutput())
        if len(self.buffer)>1024*1024:self.buffer=self.buffer[-65536:]
        while b"\n" in self.buffer:
            line,self.buffer=self.buffer.split(b"\n",1)
            try:record=json.loads(line.decode("utf-8"))
            except (ValueError,UnicodeError):continue
            if record.get("type")=="progress":self.progress.emit(record.get("value"))
            elif record.get("type")=="error":self.error=str(record.get("message","Worker failed"))[:2000]
    def read_stderr(self):
        self.stderr=(self.stderr+bytes(self.process.readAllStandardError()).decode("utf-8",errors="replace"))[-32000:]
    def process_error(self,error):
        if error==QProcess.ProcessError.FailedToStart:self.error="Could not start processing worker: "+self.process.errorString();self.exited(-1,QProcess.ExitStatus.CrashExit)
    def exited(self,code,status):
        if self.done:return
        self.done=True;self.kill_timer.stop();self.read_stdout();self.read_stderr()
        if self.stderr:(self.directory/"stderr.txt").write_text(self.stderr,encoding="utf-8")
        try:
            if code==0 and (self.directory/"result.json").exists():self.finished.emit(bounded_json(self.directory/"result.json"))
            else:
                state="cancelled" if self.cancel_requested else "crashed" if status==QProcess.ExitStatus.CrashExit else "failed"
                (self.directory/"state.json").write_text(json.dumps({"status":state,"exit_code":code}),encoding="utf-8")
                request=bounded_json(self.path)
                if request.get("operation") in ("export","climate","analysis"):
                    from .exports import safe_name
                    manifest_path=Path(request["folder"]).resolve()/safe_name(request["name"])/"manifest.json"
                    if manifest_path.is_file() and not manifest_path.is_symlink():
                        manifest=bounded_json(manifest_path)
                        if manifest.get("job_id")==self.directory.name and manifest.get("status")=="running":
                            manifest["status"]="cancelled" if self.cancel_requested else "failed"
                            manifest.setdefault("errors",[]).append({"stage":"worker","error":"Worker exited before completion","exit_code":code,"log":str(self.directory)})
                            manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
                self.failed.emit(("Cancelled" if self.cancel_requested else self.error or "Processing worker stopped unexpectedly (exit %s)."%code)+"\nLog: "+str(self.directory))
        except Exception as exc:self.failed.emit(str(exc)+"\nLog: "+str(self.directory))
        finally:self.stopped.emit()
