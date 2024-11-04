## Node behavior

Kubernetes automatically spreads the Pods for
workload resources (such as {{< glossary_tooltip text="Deployment" term_id="deployment" >}}
or {{< glossary_tooltip text="StatefulSet" term_id="statefulset" >}})
across different nodes in a cluster. This spreading helps
reduce the impact of failures.

When nodes start up, the kubelet on each node automatically adds
{{< glossary_tooltip text="labels" term_id="label" >}} to the Node object
that represents that specific kubelet in the Kubernetes API.
These labels can include
[zone information](/docs/reference/labels-annotations-taints/#topologykubernetesiozone).

If your cluster spans multiple zones or regions, you can use node labels
in conjunction with
[Pod topology spread constraints](/docs/concepts/scheduling-eviction/topology-spread-constraints/)
to control how Pods are spread across your cluster among fault domains:
regions, zones, and even specific nodes.
These hints enable the
{{< glossary_tooltip text="scheduler" term_id="kube-scheduler" >}} to place
Pods for better expected availability, reducing the risk that a correlated
failure affects your whole workload.

For example, you can set a constraint to make sure that the
3 replicas of a StatefulSet are all running in different zones to each
other, whenever that is feasible. You can define this declaratively
without explicitly defining which availability zones are in use for
each workload.

### Distributing nodes across zones

Kubernetes' core does not create nodes for you; you need to do that yourself,
or use a tool such as the [Cluster API](https://cluster-api.sigs.k8s.io/) to
manage nodes on your behalf.

Using tools such as the Cluster API you can define sets of machines to run as
worker nodes for your cluster across multiple failure domains, and rules to
automatically heal the cluster in case of whole-zone service disruption.

## Manual zone assignment for Pods

You can apply [node selector constraints](/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector)
to Pods that you create, as well as to Pod templates in workload resources
such as Deployment, StatefulSet, or Job.