# Metrics Application Helm Chart

This Helm chart deploys the Metrics application, consisting of a UI and API component.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Ingress controller installed (if using Ingress)
- PV provisioner support in the underlying infrastructure (if persistence is needed)

## Installing the Chart

To install the chart with the release name `metrics`:

```bash
helm install metrics ./metrics-chart
```

## Uninstalling the Chart

To uninstall/delete the `metrics` release:

```bash
helm uninstall metrics
```

## Configuration

The following table lists the configurable parameters of the Metrics chart and their default values.

| Parameter                      | Description                                     | Default                                      |
| ------------------------------ | ----------------------------------------------- | -------------------------------------------- |
| `global.environment`           | Environment for deployment                      | `production`                                 |
| `api.replicaCount`             | Number of API replicas                          | `2`                                          |
| `api.image.repository`         | API image repository                            | `registry.quantum-forge.net/metrics-api`   |
| `api.image.tag`                | API image tag                                   | `latest`                                     |
| `api.image.pullPolicy`         | API image pull policy                           | `Always`                                     |
| `api.service.type`             | API service type                                | `ClusterIP`                                  |
| `api.service.port`             | API service port                                | `80`                                         |
| `api.service.targetPort`       | API container port                              | `5000`                                       |
| `api.resources`                | API resource requests/limits                    | See `values.yaml`                            |
| `ui.replicaCount`             | Number of UI replicas                          | `2`                                          |
| `ui.image.repository`         | UI image repository                            | `registry.quantum-forge.net/metrics-ui`    |
| `ui.image.tag`                | UI image tag                                   | `latest`                                     |
| `ui.image.pullPolicy`         | UI image pull policy                           | `Always`                                     |
| `ui.service.type`             | UI service type                                | `ClusterIP`                                  |
| `ui.service.port`             | UI service port                                | `80`                                         |
| `ui.service.targetPort`       | UI container port                              | `3000`                                       |
| `ui.resources`                | UI resource requests/limits                    | See `values.yaml`                            |
| `ingress.enabled`              | Enable ingress resource                         | `true`                                       |
| `ingress.annotations`          | Ingress annotations                             | See `values.yaml`                            |
| `ingress.hosts`                | Ingress hosts configuration                     | See `values.yaml`                            |
| `ingress.tls`                  | Ingress TLS configuration                       | See `values.yaml`                            |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install metrics ./metrics-chart --set api.replicaCount=3,ui.replicaCount=3
```

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example:

```bash
helm install metrics ./metrics-chart -f values-prod.yaml