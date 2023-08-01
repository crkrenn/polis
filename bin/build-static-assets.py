#!/usr/bin/env python

# ported from `build-static-assets.clj` to solve problems with OS X builds

import datetime
import time
import subprocess
import sys
import os

LOCAL_DIST_DIRECTORY = "dist"
CONTAINER_DIST_DIRECTORY = "build"

uname = subprocess.run(["uname", "-a"], capture_output=True).stdout.decode().split(" ")
if uname[0] == "Darwin" and "ARM64" in uname[-2]:
  print("Running on an apple m1/m2 chip")
  DOCKER_BUILD_COMMAND = "buildx build --platform linux/amd64"
else:
  DOCKER_BUILD_COMMAND = "build"
print(f"docker build command: {DOCKER_BUILD_COMMAND}")

timestamp = datetime.datetime.now().strftime('%s')
cwd = os.getcwd()

# (defn logged-command [& args]
def logged_command(cmd_list, directory):
  os.chdir(os.path.join(cwd, directory))
  print(f"Running: {' '.join(cmd_list)}")
  p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  while p.poll() == None:
      print(p.stdout.readline().decode().strip("\n"))
  if p.returncode !=0:
    print(f"ERROR")
    sys.exit(1)

# (defn image-name [client-dir]
def image_name(client_dir):
  return f"polis/{os.path.basename(client_dir)}"

# (defn container-name [client-dir]
def container_name(client_dir):
  return f"polis-{os.path.basename(client_dir)}-cp-container-{timestamp}"

# (defn build-client
def build_client(client_dir):
  cmd_string = (f"docker {DOCKER_BUILD_COMMAND} -t "
                f"{image_name(client_dir)} .")
  logged_command(cmd_string.split(" "), client_dir)

# (defn run-client-container
def run_client_container(client_dir):
  cmd_string = (f"docker run --name {container_name(client_dir)} "
                f"{image_name(client_dir)} sleep 10")
  logged_command(cmd_string.split(" "), client_dir)


# (defn clean-build
def clean_build(client_dir):
  logged_command(f"rm -fr {LOCAL_DIST_DIRECTORY}".split(" "), client_dir)

# (defn cp-client
def cp_client(client_dir):
  cmd_string = (f"docker cp {container_name(client_dir)}:"
                f"/app/{CONTAINER_DIST_DIRECTORY}/ "
                f"{LOCAL_DIST_DIRECTORY}")
  logged_command(cmd_string.split(" "), client_dir)


# (defn monitor-execution
# Note: the clojure version offers more features
def monitor_execution(function, *arguments):
  function(*arguments)

# (defn stop-containers
def stop_containers(client_dir):
  cmd_string = f"docker stop {container_name(client_dir)}"
  logged_command(cmd_string.split(" "), client_dir)

# (defn clean-containers
def clean_containers(client_dir):
  cmd_string = f"docker rm {container_name(client_dir)}"
  logged_command(cmd_string.split(" "), client_dir)

# (defn build-and-cp-client
def build_and_cp_client(client_dir):
  monitor_execution(build_client, client_dir)
  monitor_execution(run_client_container, client_dir)
  monitor_execution(build_client, client_dir)
  monitor_execution(clean_build, client_dir)
  monitor_execution(cp_client, client_dir)
  monitor_execution(stop_containers, client_dir)
  monitor_execution(clean_containers, client_dir)

# Note: edit the "dir_list" variable by hand for partial builds
dir_list = ["client-admin", "client-report", "client-participation", ]
dir_list = ["client-admin", "client-participation", ]
for client_dir in dir_list:
  start_time = time.time()
  print(f"Building {client_dir}")
  print(f"Start time: {datetime.datetime.now()}")
  build_and_cp_client(client_dir)
  print(f"Finished with {client_dir}")
  print(f"Start time: {datetime.datetime.now()}")
  print(f"Elapsed time: {time.time() - start_time} seconds.")

# ;; QED