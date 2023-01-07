#!/usr/bin/env python

# need basename, etc. for build step

# (require '[babashka.pods :as pods]
#          '[babashka.deps :as deps]
#          '[babashka.process :as process]
#          '[clojure.core.async :as async]
#          '[clojure.pprint :as pp]
#          '[clojure.tools.cli :as cli]
#          '[clojure.java.io :as io]
#          '[clojure.string :as string])
import datetime
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

# ;; basic example using the process library
# ;(-> (process/process '[ls -a] {:dir "math"}) :out slurp)

# (def timestamp (System/currentTimeMillis))
timestamp = datetime.datetime.now().strftime('%s')
cwd = os.getcwd()

# (defn logged-command [& args]
#     (println "Executing command:" (pr-str args))
#     (apply process/process args))
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
#   (str "polis/" client-dir))
def image_name(client_dir):
  return f"polis/{os.path.basename(client_dir)}"

# (defn container-name [client-dir]
#   (str "polis-" client-dir "-cp-container-" timestamp))
def container_name(client_dir):
  return f"polis-{os.path.basename(client_dir)}-cp-container-{timestamp}"

# (defn build-client
#   "Build the client container, and give it a unique name"
#   [client-dir]
#   (logged-command ['docker 'build '-t (image-name client-dir) '.]
#                   {:dir client-dir}))
def build_client(client_dir):
  cmd_string = (f"docker {DOCKER_BUILD_COMMAND} -t "
                f"{image_name(client_dir)} .")
  logged_command(cmd_string.split(" "), client_dir)

# (defn run-client-container
#   [client-dir]
#   "Run sleep in the client container so that it is running when we try to copy stuff out of it
#   (docker cp only works when the container is running)"
#   (let [command (concat '[docker run --name]
#                         [(container-name client-dir) (image-name client-dir)]
#                         ;; we sleep in the container so that it doesn't just shut down immediately, before we
#                         ;; copy anything
#                         '[sleep 10])]
#     (logged-command command {:dir client-dir})))
def run_client_container(client_dir):
  cmd_string = (f"docker run --name {container_name(client_dir)} "
                f"{image_name(client_dir)} sleep 10")
  logged_command(cmd_string.split(" "), client_dir)


# (defn clean-build
#   "Remove local build/dist files"
#   [client-dir]
#   (logged-command '[rm -fr dist] {:dir client-dir}))
def clean_build(client_dir):
  logged_command(f"rm -fr {LOCAL_DIST_DIRECTORY}".split(" "), client_dir)

# (defn cp-client
#   "Copy contents out of the running docker image"
#   [client-dir]
#   (logged-command ['docker 'cp (str (container-name client-dir) ":/app/dist/") 'dist]
#                   {:dir client-dir}))
def cp_client(client_dir):
  cmd_string = (f"docker cp {container_name(client_dir)}:"
                f"/app/{CONTAINER_DIST_DIRECTORY}/ "
                f"{LOCAL_DIST_DIRECTORY}")
  logged_command(cmd_string.split(" "), client_dir)


# (defn monitor-execution
#   "Monitor the execution, and return an error object if the process does not execute properly"
#   [proc]
#   (let [{:keys [exit out err]} @proc]
#     (when (> exit 0)
#       (println "PROCESS FAILED TO EXECUTE SUCCESSFULLY!"))
#     (println "Exit status:" exit)
#     (let [out-str (slurp out)
#           err-str (slurp err)]
#       (when-not (empty? out-str)
#         (println "Std out" out-str))
#       (when-not (empty? err-str)
#         (println "Std err" err-str)))))
def monitor_execution(function, *arguments):
  function(*arguments)

# (defn stop-containers
#   "Stop the containers, so that we can remove them"
#   [client-dir]
#   (logged-command ['docker 'stop (container-name client-dir)]))
def stop_containers(client_dir):
  cmd_string = f"docker stop {container_name(client_dir)}"
  logged_command(cmd_string.split(" "), client_dir)

# (defn clean-containers
#   "Remove the old container to clean up after ourselves"
#   [client-dir]
#   (logged-command ['docker 'rm (container-name client-dir)]))
def clean_containers(client_dir):
  cmd_string = f"docker rm {container_name(client_dir)}"
  logged_command(cmd_string.split(" "), client_dir)



# (defn build-and-cp-client
#   "Build the clients with docker and copy out the assets"
#   [client-dir]
#   ;; build the client itself, and block till complete
#   (monitor-execution (build-client client-dir))
#   ;; start client container and let run (should have softer monitoring of this
#   (run-client-container client-dir)
#   ;; once that is started clean the build dir
#   (monitor-execution (build-client client-dir))
#   (monitor-execution (clean-build client-dir))
#   (monitor-execution (cp-client client-dir))
#   (monitor-execution (stop-containers client-dir))
#   (monitor-execution (clean-containers client-dir)))
#   ;; once that has completed,
def build_and_cp_client(client_dir):
  monitor_execution(build_client, client_dir)
  monitor_execution(run_client_container, client_dir)
  monitor_execution(build_client, client_dir)
  monitor_execution(clean_build, client_dir)
  monitor_execution(cp_client, client_dir)
  monitor_execution(stop_containers, client_dir)
  monitor_execution(clean_containers, client_dir)

# (def processes
#   (for [client-dir ["client-admin", "client-participation"]];; "client-report"]] ; leaving client-report off for now
#     (async/thread
#       (build-and-cp-client client-dir)
#       (println "Finished building:" client-dir))))

# ;; Initiate all of the processes, since for is a lazy list
# (doall processes)
# ;; for each process, wait until the process completes
# (doseq [proc processes]
#   (async/<!! proc))

# ;; QED

dir_list = ["client-admin", "client-report", "client-participation", ]
dir_list = [ "client-report", ]
for client_dir in dir_list:
  build_and_cp_client(client_dir)
  print(f"Finished with {client_dir}")
