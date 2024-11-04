A cluster is a set of {{< glossary_tooltip text="nodes" term_id="node" >}} (physical
or virtual machines) running Kubernetes agents, managed by the
{{< glossary_tooltip text="control plane" term_id="control-plane" >}}.
Kubernetes {{< param "version" >}} supports clusters with up to 5,000 nodes. More specifically,
Kubernetes is designed to accommodate configurations that meet *all* of the following criteria:

* No more than 110 pods per node
* No more than 5,000 nodes
* No more than 150,000 total pods
* No more than 300,000 total containers

You can scale your cluster by adding or removing nodes. The way you do this depends
on how your cluster is deployed.

## Cloud provider resource quotas {#quota-issues}

To avoid running into cloud provider quota issues, when creating a cluster with many nodes,
consider:
* Requesting a quota increase for cloud resources such as:
    * Computer instances
    * CPUs
    * Storage volumes
    * In-use IP addresses
    * Packet filtering rule sets
    * Number of load balancers
    * Network subnets
    * Log streams
* Gating the cluster scaling actions to bring up new nodes in batches, with a pause
  between batches, because some cloud providers rate limit the creation of new instances.

## Control plane components

For a large cluster, you need a control plane with sufficient compute and other
resources.

Typically you would run one or two control plane instances per failure zone,
scaling those instances vertically first and then scaling horizontally after reaching
the point of falling returns to (vertical) scale.

You should run at least one instance per failure zone to provide fault-tolerance. Kubernetes
nodes do not automatically steer traffic towards control-plane endpoints that are in the
same failure zone; however, your cloud provider might have its own mechanisms to do this.

For example, using a managed load balancer, you configure the load balancer to send traffic
that originates from the kubelet and Pods in failure zone _A_, and direct that traffic only
to the control plane hosts that are also in zone _A_. If a single control-plane host or
endpoint failure zone _A_ goes offline, that means that all the control-plane traffic for
nodes in zone _A_ is now being sent between zones. Running multiple control plane hosts in
each zone makes that outcome less likely.