import json
import yaml
import sys
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path


def find_files(directory, pattern):
    return list(directory.glob(pattern))

def get_cluster_name(input_path):
    config_file = find_files(Path(f'{input_path}/sos_commands/kubernetes/cluster-info/'), '*config_view')[0]
    with open(config_file, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    return data["clusters"][0]["name"]

def get_pod_pvs(namespace, pod_name):
    try:
        # Run the kubectl command to get the pods in the specified namespace
        result = subprocess.run(["kubectl", "get", "pods", "-n", namespace], capture_output=True, text=True, check=True)

        # Filter the output using grep based on the pod name pattern
        filtered_pods = subprocess.run(["grep", f'^{pod_name}.*'], input=result.stdout, capture_output=True, text=True,
                                       check=True)

        # Split the output into lines and get the first line (assuming there's only one matching pod)
        matched_pod_line = filtered_pods.stdout.strip().split('\n')[0]

        # Extract the pod name from the matched line
        matched_pod_name = matched_pod_line.split()[0]

        # Run kubectl command to get the pod details in JSON format
        result = subprocess.run(["kubectl", "-n", namespace, "get", "pod", matched_pod_name, "-o", "json"],
                                capture_output=True, text=True, check=True)
        pod_info = json.loads(result.stdout)

        volumes = pod_info["spec"].get("volumes", [])
        pvs = []
        for volume in volumes:
            if volume.get("persistentVolumeClaim"):
                pvc_name = volume["persistentVolumeClaim"]["claimName"]
                pv_info = subprocess.run(["kubectl", "-n", namespace, "get", "pvc", pvc_name, "-o", "json"],
                                         capture_output=True, text=True, check=True)
                pvc_info = json.loads(pv_info.stdout)
                pv_name = pvc_info["spec"]["volumeName"]
                pv_details = subprocess.run(["kubectl", "get", "pv", pv_name, "-o", "json"], capture_output=True,
                                            text=True, check=True)
                pv = json.loads(pv_details.stdout)
                pv_type = pv.get("spec", {}).get("storageClassName", "Unknown")
                pv_path = ""
                pv_ip = ""
                if pv_type == "nfs":
                    pv_path = pv["spec"]["nfs"]["path"]
                    pv_ip = pv["spec"]["nfs"]["server"]
                elif pv_type == "azureFile":
                    pv_path = pv["spec"]["azureFile"]["secretName"]
                elif pv_type == "awsElasticBlockStore":
                    pv_path = pv["spec"]["awsElasticBlockStore"]["volumeID"]
                elif pv_type == "local-path":
                    pv_path = pv["spec"]["hostPath"]["path"]
                    pv_ip = "None"
                elif pv_type == "csi-s3":
                    pv_path = pv["spec"]["csi"]["volumeHandle"]
                    pv_ip = "None"
                else:
                    pv_type = "Unknown"
                    pv_path = "None"
                    pv_ip = "None"
                pv_info = {
                    "pv-type": pv_type,
                    "pv-path": pv_path,
                    "pv-ip": pv_ip
                }
                pvc_info = {
                    "pvc": pvc_name,
                    "children": [pv_info]
                }
                pvs.append(pvc_info)
        return pvs
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None


def get_nodes(input_path):
    names = []
    nodes_file = find_files(Path(f'{input_path}/sos_commands/kubernetes/cluster-info/'), '*get_-o_json_nodes')[0]
    print(nodes_file)
    with open(nodes_file,
              'r') as f:
        data = json.loads(f.read())

    names = [node["metadata"]["name"] for node in data.get("items", []) if node["kind"] == "Node"]
    #for node in data["items"]:
    #    names.append(node["metadata"]["name"])

    print(names)
    return names


def get_namespaces(input_path):
    names = []
    namespaces_file = find_files(Path(f'{input_path}/sos_commands/kubernetes/cluster-info/'), '*get_namespaces')[0]

    with open(namespaces_file,
              'r') as f:
        data = f.read().splitlines()

    for namespace in data[1:]:
        names.append(namespace.split()[0])

    print(names)
    return names


def get_deployments(input_path, namespace):
    deployments = []
    deployments_file = find_files(
        Path(
            f'{input_path}/sos_commands/kubernetes/cluster-info/{namespace}'),
        f'*get_-o_json_*_deployments'
    )[0]


    with open(deployments_file,
              'r') as f:
        data = json.loads(f.read())

    for item in data.get("items", []):
        if item["kind"] == "Deployment":
            deployment_info = {
                "uid": item["metadata"]["uid"],
                "namespace": item["metadata"]["namespace"],
                "type": "deployment",
                "name": item["metadata"]["name"],
                "children": get_deployment_pods(input_path, item["metadata"]["uid"], item["metadata"]["namespace"])
            }

            deployments.append(deployment_info)

    print(deployments)
    return deployments

def get_deployment_pods(input_path, deployment_uid, namespace):
    pods = []

    replicasets_file = find_files(
        Path(
            f'{input_path}/sos_commands/kubernetes/cluster-info/{namespace}'),
        f'*get_-o_json_*_replicasets'
    )[0]

    with open(replicasets_file,
                'r') as f:
        replicaset_data = json.loads(f.read())



    pods_file = find_files(
        Path(
            f'{input_path}/sos_commands/kubernetes/cluster-info/{namespace}'),
        f'*get_-o_json_*_pods'
    )[0]

    with open(pods_file,
              'r') as f:
        data = json.loads(f.read())

    deployment_replicasets = []
    for item in replicaset_data.get("items", []):
        if item["metadata"]["ownerReferences"][0]["uid"] == deployment_uid:
            deployment_replicasets.append(item["metadata"]["uid"])

    for item in data.get("items", []):
        print(item)
        if item["kind"] == "Pod" and 'ownerReferences' in  item['metadata']:
            if item["metadata"]["ownerReferences"][0]["uid"] in deployment_replicasets:
                pod_info = {
                    'uid': item["metadata"]["uid"],
                    "type": "pod",
                    "name": item["metadata"]["name"],
                  #  "pv_name": get_pod_pvs(namespace, item["metadata"]["name"])
                }
                pods.append(pod_info)

    print(pods)
    return pods


def format_json(input_path, output_file):
    data = {}
    # with open(input_file, 'r') as f:
    #   data = json.load(f)

    # node_names = [node["metadata"]["name"] for node in data.get("items", []) if node["kind"] == "Node"]
    node_names = get_nodes(input_path)
    namespaces = get_namespaces(input_path)

    formatted_data = {
        "nodes": node_names,
        "namecluster": get_cluster_name(input_path),
        "children": []
    }

    for namespace in namespaces:
        deployments = get_deployments(input_path, namespace)
        formatted_data["children"].extend(deployments)

    #for item in data.get("items", []):
    #    if item["kind"] == "Deployment":
    # #       deployment_info = {
    #            "namespace": item["metadata"]["namespace"],
    #            "type": "deployment",
    #            "name": item["metadata"]["name"],
    #            "children": []
    #        }
    #        for pod_status in item.get("status", {}).get("conditions", []):
    #            if pod_status["type"] == "Progressing":
    #                message = pod_status.get("message", "")
    #                match = re.search(r'ReplicaSet "([^"]+)" has successfully progressed.', message)
    #                if match:
    #                    pod_name = match.group(1)
    #                    pod_info = {
    #                        "type": "pod",
    #                        "name": pod_name,
    #                        "pv_name": get_pod_pvs(item["metadata"]["namespace"], pod_name)
    #                    }
    #                    deployment_info["children"].append(pod_info)
    #        formatted_data["children"].append(deployment_info)

    with open(output_file, 'w') as f:
        json.dump(formatted_data, f, indent=4)


def extract_sos_archive(archive_path):
    tmp_dir = tempfile.mkdtemp()

    with tarfile.open(archive_path, 'r:xz') as tar:
        members = []
        for member in tar.getmembers():
            p = Path(member.path)
            member.path = p.relative_to(*p.parts[:1])
            members.append(member)

        tar.extractall(path=tmp_dir, members=members)

    return tmp_dir


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file.json> <output_file.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    tmp_dir = extract_sos_archive(input_file)

    print("Extracted sosreport archive to:", tmp_dir)

    output_file = sys.argv[2] if (len(sys.argv) > 2) else "output.json"

    format_json(tmp_dir, output_file)
