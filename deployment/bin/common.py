def call_cmd(cmd):
    LOG.debug(cmd)
    # result = subprocess.run(cmd, shell=True, capture_output=True)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        if not line and p.poll() != None:
            break
        if line:
            stdout.append(line.decode("utf-8"))
            LOG.info(line.decode("utf-8").strip())
    if p.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=p.returncode,
            cmd=cmd,
            output="".join(stdout),
            stderr=None
            )
    return p


def dict_extract(key, var):
    if hasattr(var,'items'): # hasattr(var,'items') for python 3
        for k, v in var.items(): # var.items() for python 3
            if k == key:
                yield var
            if isinstance(v, dict):
                for result in dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract(key, d):
                        yield result

def add_elements_to_item(item_key, dictionary, tags):
    print(f"Adding the following '{item_key}' to the cloud compose definition: {tags}")
    results = dict_extract(item_key, dictionary)
    for result in results:
        for key, value in tags.items():
            if type(result[item_key]) == list:
                result[item_key].append({'Key': key, 'Value': value})
            elif type(result[item_key]) == dict:
                result[item_key][key] = value
            else:
                raise ValueError("type must be list or dict")

def update_keys(dictionary, new_keys):
    print(f"Making the following updates to the cloud compose definition: {new_keys}")
    for key, value in new_keys.items():
        results = dict_extract(key, dictionary)
        for result in results:
            result[key] = value

def delete_keys(dictionary, keys):
    print(f"Deleting the following elements fromthe cloud compose definition: {keys}")
    for key in keys:
        results = dict_extract(key, dictionary)
        while results:
            result = next(results, None)
            if result:
                del result[key]
                results = dict_extract(key, dictionary)
            else:
                results = None
