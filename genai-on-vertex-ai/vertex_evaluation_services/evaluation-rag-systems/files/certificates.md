## Where certificates are stored

If you install Kubernetes with kubeadm, most certificates are stored in `/etc/kubernetes/pki`.
All paths in this documentation are relative to that directory, with the exception of user account
certificates which kubeadm places in `/etc/kubernetes`.

## Configure certificates manually

If you don't want kubeadm to generate the required certificates, you can create them using a
single root CA or by providing all certificates. See [Certificates](/docs/tasks/administer-cluster/certificates/)
for details on creating your own certificate authority. See
[Certificate Management with kubeadm](/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/)
for more on managing certificates.

### Single root CA

You can create a single root CA, controlled by an administrator. This root CA can then create
multiple intermediate CAs, and delegate all further creation to Kubernetes itself.

Required CAs:

| path                   | Default CN                | description                      |
|------------------------|---------------------------|----------------------------------|
| ca.crt,key             | kubernetes-ca             | Kubernetes general CA            |
| etcd/ca.crt,key        | etcd-ca                   | For all etcd-related functions   |
| front-proxy-ca.crt,key | kubernetes-front-proxy-ca | For the [front-end proxy](/docs/tasks/extend-kubernetes/configure-aggregation-layer/) |

On top of the above CAs, it is also necessary to get a public/private key pair for service account
management, `sa.key` and `sa.pub`.
The following example illustrates the CA key and certificate files shown in the previous table:

```
/etc/kubernetes/pki/ca.crt
/etc/kubernetes/pki/ca.key
/etc/kubernetes/pki/etcd/ca.crt
/etc/kubernetes/pki/etcd/ca.key
/etc/kubernetes/pki/front-proxy-ca.crt
/etc/kubernetes/pki/front-proxy-ca.key
```