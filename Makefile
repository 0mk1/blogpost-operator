setup: namespace crd rbac deploy

build-image:
	docker build . -t t0ffi9/blogpost-operator:latest

push-image:
	docker push t0ffi9/blogpost-operator:latest

minikube:
	minikube start --kubernetes-version=v1.14.3 --vm-driver=hyperkit --extra-config=apiserver.authorization-mode=RBAC

namespace:
	kubectl apply -f ./namespace.yml
	kubens blogposts

crd:
	kubectl apply -f ./crds

rbac:
	kubectl apply -f ./rbac.yml

deploy:
	kubectl apply -f ./deploy.yml

test-resource:
	kubectl apply -f ./test/blogpostrequest.yml

cleanup:
	kubectl delete -f ./deploy.yml
	kubectl delete -f ./rbac.yml
	kubectl delete -f ./namespace.yml
	kubectl delete -f ./crds
