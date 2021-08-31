import sys, time, queue, neovim, json, os, re, subprocess, pickle, threading, socket, signal
from os.path import expanduser
# sys.path.append('.cache')
# from config import cur, compileCmd, codePath, templatePath, regrexLink
exec(open("/tmp/cp.conf").read())
problemList = []
problemStatus = {}
problem = {}

nvim = neovim.attach('socket', path = '/tmp/cp')
vim = queue.Queue()
def vim_send():
  while True:
    s = vim.get()
    nvim.command(s)
 
class Problem:
  def __init__(self, problemPath, curTest, timeout):
    self.problemPath = problemPath
    self.curTest = curTest
    self.result = {}
    self.timeout = timeout

  def tabline(self):
    s = ""
    for i in range(len(problemList)):
      s += "%#fNA#" if cur == problemList[i] else "%#NA#" # TODO : submit status
      s += f"%{i}@CpTab@\ {problemList[i]}\ "
    s += "%#TabLineFill#%T%="

    for i, v in self.result.items():
      s += "%#" + ("f" if i == self.curTest else "") + v + "#"
      s += f"%{i}@CpTest@"
      s += f"\ {i}\ "
    vim.put(f"set tabline={s}")

  def submit(self):
    os.system("echo [Submitting...] > .info")
    vim.put("let i = winnr() | 2wincmd w | e .info | execute i . 'wincmd w'")
    os.system(f"cf submit -f sol.cpp {cur} > .info")
    vim.put("let i = winnr() | 2wincmd w | e | execute i . 'wincmd w'")

  def test(self, t):
    if not t in self.result: return
    vim.put(f"let i = winnr() | 2wincmd w | e tests/{t}/.stderr | 3wincmd w | e tests/{t}/{t}.in | 4wincmd w | e tests/{t}/{t}.out | 5wincmd w | e tests/{t}/{t}.ans | execute i . 'wincmd w'")
    self.curTest = t
    self.tabline()

  def add(self, t):
    self.result[t] = "NA"
    os.system(f"mkdir tests/{t}")
    os.system(f"touch tests/{t}/{t}.in")
    os.system(f"touch tests/{t}/{t}.ans")
    self.test(t)

  def remove(self, t):
    os.system(f"rm -r tests/{t}")
    self.result.pop(t)
    self.tabline()

  def hide_show(self, t):
    if self.result[t] == "HD":
      self.result[t] = "NA"
    else:
      self.result[t] = "HD"
    self.tabline()

  def show_all(self):
    for t, v in self.result.items():
      if self.result[t] == "HD":
        self.result[t] = "NA"
    self.tabline()

  def invert(self):
    for t, v in self.result.items():
      if self.result[t] == "HD":
        self.result[t] = "NA"
      else:
        self.result[t] = "HD"
    self.tabline()

  def hide(self, stat):
    for t, v in self.result.items():
      if v == stat:
        self.result[t] = "HD"
    self.tabline()

  def compile(self):
    os.system("rm -rf sol; echo [Complication has started] > .info")
    startTime = time.time()
    vim.put("let i = winnr() | 2wincmd w | edit .info | execute i . 'wincmd w'")
    for t, v in self.result.items():
      if self.result[t] != 'HD':
        self.result[t] = "NA"
    self.tabline()
    os.system(f"{compileCmd} sol.cpp -o {self.problemPath}/sol 2>> .info")
    if os.path.isfile("sol"):
      os.system(f"echo [Complication has finished in {round(time.time() - startTime, 2)}s] >> .info")
    else:
      os.system(f"echo [Compile error] >> .info")
    vim.put("let i = winnr() | 2wincmd w | e | execute i . 'wincmd w'")

  def run(self, t):
    self.result[t] = "PD"
    proc = subprocess.Popen(f"exec ./sol < tests/{t}/{t}.in > tests/{t}/{t}.out 2> tests/{t}/.stderr", shell = True)
    try: proc.communicate(timeout = self.timeout)
    except subprocess.TimeoutExpired:
      proc.kill()
      self.result[t] = "TL"
      self.tabline()
      return
    if proc.returncode:
      self.result[t] = "RE"
    else:
      if subprocess.run(f"diff -qbB tests/{t}/{t}.out tests/{t}/{t}.ans", shell = True).returncode:
        self.result[t] = "WA"
      else:
        self.result[t] = "AC"
    self.tabline()
  
  def run_all(self):
    process = []
    for t, v in self.result.items():
      if self.result[t] == 'HD':
        continue
      p = threading.Thread(target = self.run, args = (t, ))
      p.start()
      process.append(p)
    for p in process:
      p.join()
    vim.put(f"let i = winnr() | 2 wincmd w | e! | 4wincmd w | e! | execute i . 'wincmd w'")

  def compile_run(self):
    self.compile()
    if not os.path.isfile("sol"):
      return
    vim.put(f"let i = winnr() | 2wincmd w | e! tests/{self.curTest}/.stderr | execute i . 'wincmd w'")
    self.run_all()

  def build(self, tests):
    os.system(f"mkdir -p {self.problemPath}/tests/0")
    os.chdir(self.problemPath)
    os.system(f"cp -n {templatePath} sol.cpp")

    for i in range(0, len(tests)):
      self.result[i] = "NA"
      os.system(f"mkdir tests/{i}")
      with open(f"tests/{i}/{i}.in", "w") as f:
        f.write(tests[i]['input'])
      with open(f"tests/{i}/{i}.ans", "w") as f:
        f.write(tests[i]['output'])

  def display(self):
    os.chdir(self.problemPath)
    vim.put(f"cd {problem[cur].problemPath} | vs | edit sol.cpp | setl wfw | wincmd w | bel sp | vs | vs")
    self.test(self.curTest)
    self.tabline()

def tab(t):
  global cur
  cur = problemList[int(t)]
  vim.put(f"tabn {int(t) + 1}")
  os.chdir(problem[cur].problemPath)
  vim.put(f"cd {problem[cur].problemPath}")
  problem[cur].tabline()

def build(problemInfo):
  for link in regrexLink:
    match = re.match(link, problemInfo['url'])
    if match:
      contestId = match.group(1)
      problemCode = match.group(2)

  global cur
  cur = contestId + problemCode
  if cur in problemStatus:
    return
  if problemList:
    vim.put("tabnew")
  problemStatus[cur] = "NA"
  problemList.append(cur)
  problemPath = f"{codePath}/{contestId}/{problemCode}"
  if os.path.isfile(f"{problemPath}/.{cur}"):
    with open(f"{problemPath}/.{cur}", "rb") as f:
      problem[cur] = pickle.load(f)
  else:
    problem[cur] = Problem(problemPath, 0, problemInfo['timeLimit'] / 1000)
    problem[cur].build(problemInfo['tests'])
  problem[cur].display()

def save_quit():
  for n, p in problem.items():
    with open(f"{p.problemPath}/.{n}", "wb") as f:
      pickle.dump(p, f)
  os._exit(0)

# Competitive Companion
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 10045

class Handler(BaseHTTPRequestHandler):
  def do_POST(self):
    content_len = int(self.headers['Content-Length'])
    post_body = self.rfile.read(content_len)
    build(json.loads(post_body))
    vim.put("set showtabline=2 | set hidden | set autoread")

  def log_message(self, format, *args):
    return

def http_listen(server_class = HTTPServer, handler_class = Handler, port = PORT):
  server_address = ('', port)
  httpd = server_class(server_address, handler_class)
  try:
    httpd.serve_forever()
  except:
    pass

def vim_listen(s = socket.socket()):
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('127.0.0.1', 11713))
  s.listen()
  while True:
    try:
      eval(s.accept()[0].recv(1024).decode())
    except:
      vim.put("echo \"Invalid function\"")

if __name__ == '__main__':
  threading.Thread(target = vim_send).start()
  threading.Thread(target = http_listen).start()
  threading.Thread(target = vim_listen).start()
