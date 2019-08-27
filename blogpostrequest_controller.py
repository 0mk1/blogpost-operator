import requests

from kubernetes import client, config, watch


def main():
    config.load_incluster_config()
    crds = client.CustomObjectsApi()

    print("Operator started...")
    resource_version = ""
    while True:
        stream = watch.Watch().stream(
            crds.list_namespaced_custom_object,
            "merixstudio.com",
            "v1",
            "blogposts",
            "blogpostrequests",
            resource_version=resource_version,
        )
        for event in stream:
            event_type = event["type"]
            obj = event["object"]
            print(event_type)
            print(obj)
            spec = obj.get("spec")
            metadata = obj.get("metadata")
            resource_version = metadata["resourceVersion"]

            if event_type != "ADDED":
                continue

            try:
                params = {"paras": spec.get("paragraphs")}
                resp = requests.get(url="http://hipsterjesus.com/api/", params=params)
                data = resp.json()
                body = data["text"]
                print(body)
                resp = crds.create_namespaced_custom_object(
                    "merixstudio.com",
                    "v1",
                    "blogposts",
                    "blogposts",
                    {
                        "apiVersion": "merixstudio.com/v1",
                        "kind": "BlogPost",
                        "metadata": client.V1ObjectMeta(name=metadata.get("name")),
                        "spec": {"title": spec.get("title"), "body": body},
                    },
                )
                print(resp)
            except Exception as e:
                print("Error:", e)
                break
    print("Bye Bye...")


if __name__ == "__main__":
    main()
