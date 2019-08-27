import requests
from kubernetes import client, config, watch


def main():
    config.load_incluster_config()
    crds = client.CustomObjectsApi()

    stream = watch.Watch().stream(
        crds.list_namespaced_custom_object,
        "merixstudio.com",
        "v1",
        "blogposts",
        "blogpostrequests",
    )
    for event in stream:
        obj = event["object"]
        spec = obj.get("spec")
        print(spec)
        params = {
            "paras": spec.get('paragraphs')
        }
        resp = requests.get(url="http://hipsterjesus.com/api/", params=params)
        data = resp.json()
        body = data['text']
        print(body)

    print("blogpost-operator dies...")


if __name__ == '__main__':
    main()
