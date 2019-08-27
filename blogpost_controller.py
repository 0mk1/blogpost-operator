import html

from kubernetes import client, config, watch


def create_configmap(blogpost_name, title, body):
    data = {
        "default.conf": """
server {{
  listen 80;
  server_name _;
  add_header Content-Type text/html;

  location / {{
    return 200 '<html>
      <head>
        <title>{title}</title>
      </head>
      <body bgcolor="yellow">
        <marquee><h1>{title}</h1></marquee>
        <p align="center">{body}</p>
      </body>
    </html>';
  }}
}}
        """.format(
            title=html.escape(title), body=html.escape(body)
        )
    }
    return client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(name=f"{blogpost_name}"),
        data=data,
    )


def create_nginx_deployment(blogpost_name):
    container = client.V1Container(
        name="nginx",
        image="nginx:alpine",
        ports=[client.V1ContainerPort(container_port=80)],
        volume_mounts=[
            client.V1VolumeMount(name="config", mount_path="/etc/nginx/conf.d")
        ],
    )
    volume = client.V1Volume(
        name="config",
        config_map=client.V1ConfigMapVolumeSource(name=f"{blogpost_name}"),
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": f"nginx-{blogpost_name}"}),
        spec=client.V1PodSpec(containers=[container], volumes=[volume]),
    )
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={"matchLabels": {"app": f"nginx-{blogpost_name}"}},
    )

    return client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=f"nginx-{blogpost_name}"),
        spec=spec,
    )


def main():
    config.load_incluster_config()
    crds = client.CustomObjectsApi()
    apps_v1 = client.AppsV1Api()
    v1 = client.CoreV1Api()

    print("Operator started...")
    resource_version = ""
    w = watch.Watch()

    while True:
        stream = w.stream(
            crds.list_namespaced_custom_object,
            "merixstudio.com",
            "v1",
            "blogposts",
            "blogposts",
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
            name = metadata["name"]

            if event_type != "ADDED":
                continue

            try:
                cm = create_configmap(name, spec.get("title"), spec.get("body"))
                resp = v1.create_namespaced_config_map(body=cm, namespace="blogposts")
                print(resp)
                deployment = create_nginx_deployment(name)
                resp = apps_v1.create_namespaced_deployment(
                    body=deployment, namespace="blogposts"
                )
                print(resp)
            except Exception as e:
                print("Error:", e)
                break
    print("Bye Bye...")


if __name__ == "__main__":
    main()
