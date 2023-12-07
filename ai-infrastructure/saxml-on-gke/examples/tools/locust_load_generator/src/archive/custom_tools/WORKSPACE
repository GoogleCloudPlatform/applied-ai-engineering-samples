"""WORKSPACE file for Saxml."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "bazel_skylib",
    sha256 = "74d544d96f4a5bb630d465ca8bbcfe231e3594e5aae57e1edbf17a6eb3ca2506",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-skylib/releases/download/1.3.0/bazel-skylib-1.3.0.tar.gz",
        "https://github.com/bazelbuild/bazel-skylib/releases/download/1.3.0/bazel-skylib-1.3.0.tar.gz",
    ],
)

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")

bazel_skylib_workspace()

http_archive(
    name = "rules_python",
    sha256 = "8c8fe44ef0a9afc256d1e75ad5f448bb59b81aba149b8958f02f7b3a98f5d9b4",
    strip_prefix = "rules_python-0.13.0",
    url = "https://github.com/bazelbuild/rules_python/archive/refs/tags/0.13.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "python_register_toolchains")

python_register_toolchains(
    name = "python3_10",
    ignore_root_user_error = True,
    python_version = "3.10",
)

load("@python3_10//:defs.bzl", "interpreter")
load("@rules_python//python:pip.bzl", "pip_parse")

pip_parse(
    name = "third_party",
    python_interpreter_target = interpreter,
    requirements_lock = "//:requirements.txt",
)

load("@third_party//:requirements.bzl", "install_deps")

install_deps()

http_archive(
    name = "pybind11_bazel",
    sha256 = "516c1b3a10d87740d2b7de6f121f8e19dde2c372ecbfe59aef44cd1872c10395",
    strip_prefix = "pybind11_bazel-72cbbf1fbc830e487e3012862b7b720001b70672",
    urls = ["https://github.com/pybind/pybind11_bazel/archive/72cbbf1fbc830e487e3012862b7b720001b70672.tar.gz"],
)

http_archive(
    name = "pybind11",
    build_file = "@pybind11_bazel//:pybind11.BUILD",
    strip_prefix = "pybind11-2.10.1",
    urls = [
        "https://github.com/pybind/pybind11/archive/v2.10.1.tar.gz",
    ],
)

load("@pybind11_bazel//:python_configure.bzl", "python_configure")

python_configure(
    name = "local_config_python",
    python_interpreter_target = interpreter,
)

http_archive(
    name = "pybind11_abseil",
    sha256 = "be5da399b4f62615fdc2a236674638480118f6030d7b16645c6d3f0e208a7f8f",
    strip_prefix = "pybind11_abseil-1bb411eb1b13440d5af61660e70e8c5b5b2998a1",
    urls = ["https://github.com/pybind/pybind11_abseil/archive/1bb411eb1b13440d5af61660e70e8c5b5b2998a1.zip"],
)

http_archive(
    name = "pybind11_protobuf",
    sha256 = "6fa6bcf36aa54087733746a2c41b82e848b120b43576b43e4ab124315539efd7",
    strip_prefix = "pybind11_protobuf-a50899c2eb604fc5f25deeb8901eff6231b8b3c0",
    urls = ["https://github.com/pybind/pybind11_protobuf/archive/a50899c2eb604fc5f25deeb8901eff6231b8b3c0.zip"],
)

http_archive(
    name = "io_bazel_rules_go",
    sha256 = "6dc2da7ab4cf5d7bfc7c949776b1b7c733f05e56edc4bcd9022bb249d2e2a996",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_go/releases/download/v0.39.1/rules_go-v0.39.1.zip",
        "https://github.com/bazelbuild/rules_go/releases/download/v0.39.1/rules_go-v0.39.1.zip",
    ],
)

http_archive(
    name = "bazel_gazelle",
    sha256 = "727f3e4edd96ea20c29e8c2ca9e8d2af724d8c7778e7923a854b2c80952bc405",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-gazelle/releases/download/v0.30.0/bazel-gazelle-v0.30.0.tar.gz",
        "https://github.com/bazelbuild/bazel-gazelle/releases/download/v0.30.0/bazel-gazelle-v0.30.0.tar.gz",
    ],
)

http_archive(
    name = "com_google_protobuf",
    sha256 = "930c2c3b5ecc6c9c12615cf5ad93f1cd6e12d0aba862b572e076259970ac3a53",
    strip_prefix = "protobuf-3.21.12",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v3.21.12.tar.gz"],
)

http_archive(
    name = "com_github_grpc_grpc",
    sha256 = "edf25f4db6c841853b7a29d61b0980b516dc31a1b6cdc399bcf24c1446a4a249",
    strip_prefix = "grpc-%s" % "1.47.0",
    urls = ["https://github.com/grpc/grpc/archive/v%s.zip" % "1.47.0"],
)

load("@io_bazel_rules_go//go:deps.bzl", "go_register_toolchains", "go_rules_dependencies")
load("@bazel_gazelle//:deps.bzl", "gazelle_dependencies", "go_repository")
load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
load("@com_github_grpc_grpc//bazel:grpc_deps.bzl", "grpc_deps")

go_repository(
    name = "org_golang_x_net",
    importpath = "golang.org/x/net",
    sum = "h1:a8jGStKg0XqKDlKqjLrXn0ioF5MH36pT7Z0BRTqLhbk=",
    version = "v0.0.0-20210503060351-7fd8e65b6420",
)

go_repository(
    name = "org_golang_x_oauth2",
    importpath = "golang.org/x/oauth2",
    sum = "h1:RerP+noqYHUQ8CMRcPlC2nvTa4dcBIjegkuWdcUDuqg=",
    version = "v0.0.0-20211104180415-d3ed0bb246c8",
)

go_repository(
    name = "org_golang_x_sys",
    importpath = "golang.org/x/sys",
    sum = "h1:nc5K6ox/4lTFbMVSL9WRR81ixkcwXThoiF6yf+R9scA=",
    version = "v0.0.0-20200331124033-c3d80250170d",
)

go_repository(
    name = "org_golang_x_text",
    importpath = "golang.org/x/text",
    sum = "h1:g61tztE5qeGQ89tm6NTjjM9VPIm088od1l6aSorWRWg=",
    version = "v0.3.0",
)

go_repository(
    name = "org_golang_google_grpc",
    build_file_proto_mode = "disable",
    importpath = "google.golang.org/grpc",
    sum = "h1:bO/TA4OxCOummhSf10siHuG7vJOiwh7SpRpFZDkOgl4=",
    version = "v1.28.0",
)

go_repository(
    name = "org_golang_google_api",
    importpath = "google.golang.org/api",
    sum = "h1:m5FLEd6dp5CU1F0tMWyqDi2XjchviIz8ntzOSz7w8As=",
    version = "v0.52.0",
)

go_repository(
    name = "com_github_googleapis_gax_go_v2",
    importpath = "github.com/googleapis/gax-go/v2",
    sum = "h1:sjZBwGj9Jlw33ImPtvFviGYvseOtDM7hkSKB7+Tv3SM=",
    version = "v2.0.5",
)

go_repository(
    name = "com_google_cloud_go",
    importpath = "cloud.google.com/go",
    sum = "h1:MZ2cf9Elnv1wqccq8ooKO2MqHQLc+ChCp/+QWObCpxg=",
    version = "v0.88.0",
)

go_repository(
    name = "com_google_cloud_go_storage",
    importpath = "cloud.google.com/go/storage",
    sum = "h1:STgFzyU5/8miMl0//zKh2aQeTyeaUH3WN9bSUiJ09bA=",
    version = "v1.10.0",
)

go_repository(
    name = "io_opencensus_go",
    importpath = "go.opencensus.io",
    sum = "h1:gqCw0LfLxScz8irSi8exQc7fyQ0fKQU/qnC/X8+V/1M=",
    version = "v0.23.0",
)

go_repository(
    name = "com_github_golang_groupcache",
    importpath = "github.com/golang/groupcache",
    sum = "h1:1r7pUrabqp18hOBcwBwiTsbnFeTZHV9eER/QT5JVZxY=",
    version = "v0.0.0-20200121045136-8c9f03a8e57e",
)

go_repository(
    name = "com_github_golang_glog",
    importpath = "github.com/golang/glog",
    sum = "h1:VKtxabqXZkF25pY9ekfRL6a582T4P37/31XEstQ5p58=",
    version = "v0.0.0-20160126235308-23def4e6c14b",
)

go_repository(
    name = "com_github_cenkalti_backoff",
    importpath = "github.com/cenkalti/backoff",
    sum = "h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=",
    version = "v2.2.1+incompatible",
)

go_repository(
    name = "com_github_google_go_cmp",
    importpath = "github.com/google/go-cmp",
    sum = "h1:e6P7q2lk1O+qJJb4BtCQXlK8vWEO8V1ZeuEdJNOqZyg=",
    version = "v0.5.8",
)

go_repository(
    name = "com_github_google_subcommands",
    importpath = "github.com/google/subcommands",
    sum = "h1:8nlgEAjIalk6uj/CGKCdOO8CQqTeysvcW4RFZ6HbkGM=",
    version = "v1.0.2-0.20190508160503-636abe8753b8",
)

go_repository(
    name = "com_github_olekukonko_tablewriter",
    importpath = "github.com/olekukonko/tablewriter",
    sum = "h1:vHD/YYe1Wolo78koG299f7V/VAS08c6IpCLn+Ejf/w8=",
    version = "v0.0.4",
)

go_repository(
    name = "com_github_mattn_go_runewidth",
    importpath = "github.com/mattn/go-runewidth",
    sum = "h1:Ei8KR0497xHyKJPAv59M1dkC+rOZCMBJ+t3fZ+twI54=",
    version = "v0.0.7",
)

go_repository(
    name = "com_github_google_safehtml",
    importpath = "github.com/google/safehtml",
    sum = "h1:EwLKo8qawTKfsi0orxcQAZzu07cICaBeFMegAU9eaT8=",
    version = "v0.1.0",
)

go_repository(
    name = "com_github_pborman_uuid",
    importpath = "github.com/pborman/uuid",
    sum = "h1:J7Q5mO4ysT1dv8hyrUGHb9+ooztCXu1D8MY8DZYsu3g=",
    version = "v1.2.0",
)

go_repository(
    name = "com_github_google_uuid",
    importpath = "github.com/google/uuid",
    sum = "h1:t6JiXgmwXMjEs8VusXIJk2BXHsn+wx8BZdTaoZ5fu7I=",
    version = "v1.3.0",
)

go_repository(
    name = "com_github_myzhan_boomer",
    importpath = "github.com/myzhan/boomer",
    sum = "h1:xjgvmhDjgU9IEKnB7nU1HyoVEfj8SuuU3u6oY3Nugj0=",
    version = "v1.6.0",
)

go_repository(
    name = "com_github_asaskevich_eventbus",
    importpath = "github.com/asaskevich/EventBus",
    sum = "h1:2JGTg6JapxP9/R33ZaagQtAM4EkkSYnIAlOG5EI8gkM=",
    version = "v0.0.0-20200907212545-49d423059eef",
)

go_repository(
    name = "com_github_zeromq_gomq",
    importpath = "github.com/zeromq/gomq",
    sum = "h1:vGjfCnWv/zWeO1ivv4+OUPgTzG/WV1iGfZwVdtUpLkM=",
    version = "v0.0.0-20201031135124-cef4e507bb8e",
)

go_repository(
    name = "com_github_zeromq_gomq_zmtp",
    importpath = "github.com/zeromq/gomq/zmtp",
    sum = "h1:pjp04/sSr2TYuaPdt+u6Cc1M38Aocp+3er0akr3auFg=",
    version = "v0.0.0-20201031135124-cef4e507bb8e",
)

go_repository(
    name = "com_github_ugorji_go_codec",
    importpath = "github.com/ugorji/go/codec",
    sum = "h1:BMaWp1Bb6fHwEtbplGBGJ498wD+LKlNSl25MjdZY4dU=",
    version = "v1.2.11",
)

go_repository(
    name = "com_github_shirou_gopsutil",
    importpath = "github.com/shirou/gopsutil",
    sum = "h1:+1+c1VGhc88SSonWP6foOcLhvnKlUeu/erjjvaPEYiI=",
    version = "v3.21.11+incompatible",
)

go_repository(
    name = "com_github_tklauser_go_sysconf",
    importpath = "github.com/tklauser/go-sysconf",
    sum = "h1:0QaGUFOdQaIVdPgfITYzaTegZvdCjmYO52cSFAEVmqU=",
    version = "v0.3.12",
)

go_repository(
    name = "com_github_tklauser_numcpus",
    importpath = "github.com/tklauser/numcpus",
    sum = "h1:ng9scYS7az0Bk4OZLvrNXNSAO2Pxr1XXRAPyjhIx+Fk=",
    version = "v0.6.1",
)

go_rules_dependencies()

go_register_toolchains(version = "1.20.6")

gazelle_dependencies()

protobuf_deps()

grpc_deps()

# Do not run grpc_extra_deps because it registers a conflicting Go toolchain.
# Instead, directly run relevant content of grpc_extra_deps.

load("@build_bazel_rules_apple//apple:repositories.bzl", "apple_rules_dependencies")

apple_rules_dependencies()

load("@build_bazel_apple_support//lib:repositories.bzl", "apple_support_dependencies")

apple_support_dependencies()

http_archive(
    name = "com_google_googleapis",
    build_file = "@com_github_googleapis_google_cloud_cpp//bazel:googleapis.BUILD",
    sha256 = "a53e15405f81d5a32594d7f6486e649131fadda5431cf28377dff4ae54d45d16",
    strip_prefix = "googleapis-d4d09eb3aec152015f35717102f9b423988b94f7",
    urls = [
        "https://storage.googleapis.com/mirror.tensorflow.org/github.com/googleapis/googleapis/archive/d4d09eb3aec152015f35717102f9b423988b94f7.zip",
        "https://github.com/googleapis/googleapis/archive/d4d09eb3aec152015f35717102f9b423988b94f7.zip",
    ],
)

load("@com_google_googleapis//:repository_rules.bzl", "switched_rules_by_language")

switched_rules_by_language(
    name = "com_google_googleapis_imports",
    cc = True,
    grpc = True,
    python = True,
)

http_archive(
    name = "rules_cc",
    sha256 = "35f2fb4ea0b3e61ad64a369de284e4fbbdcdba71836a5555abb5e194cf119509",
    strip_prefix = "rules_cc-624b5d59dfb45672d4239422fa1e3de1822ee110",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_cc/archive/624b5d59dfb45672d4239422fa1e3de1822ee110.tar.gz",
        "https://github.com/bazelbuild/rules_cc/archive/624b5d59dfb45672d4239422fa1e3de1822ee110.tar.gz",
    ],
)

load("@rules_cc//cc:repositories.bzl", "rules_cc_dependencies")

rules_cc_dependencies()

http_archive(
    name = "com_google_absl",
    strip_prefix = "abseil-cpp-98eb410c93ad059f9bba1bf43f5bb916fc92a5ea",
    urls = ["https://github.com/abseil/abseil-cpp/archive/98eb410c93ad059f9bba1bf43f5bb916fc92a5ea.zip"],
)

http_archive(
    name = "com_google_googletest",
    strip_prefix = "googletest-011959aafddcd30611003de96cfd8d7a7685c700",
    urls = ["https://github.com/google/googletest/archive/011959aafddcd30611003de96cfd8d7a7685c700.zip"],
)

http_archive(
    name = "darts_clone",
    build_file = "//saxml/server/tf/darts_clone:BUILD",
    sha256 = "c97f55d05c98da6fcaf7f9ecc6a6dc6bc5b18b8564465f77abff8879d446491c",
    strip_prefix = "darts-clone-e40ce4627526985a7767444b6ed6893ab6ff8983",
    urls = ["https://github.com/s-yata/darts-clone/archive/e40ce4627526985a7767444b6ed6893ab6ff8983.zip"],
)

http_archive(
    name = "com_google_sentencepiece",
    build_file = "//saxml/server/tf/sentencepiece:BUILD",
    patch_args = ["-p1"],
    patches = ["//saxml/server/tf/sentencepiece:sp.patch"],
    sha256 = "8409b0126ebd62b256c685d5757150cf7fcb2b92a2f2b98efb3f38fc36719754",
    strip_prefix = "sentencepiece-0.1.96",
    urls = ["https://github.com/google/sentencepiece/archive/refs/tags/v0.1.96.zip"],
)

http_archive(
    name = "com_google_paxml",
    strip_prefix = "paxml-7002d940abbfb38e0cfe40be2847859c68f45c7a",
    urls = ["https://github.com/google/paxml/archive/7002d940abbfb38e0cfe40be2847859c68f45c7a.zip"],
)

http_archive(
    name = "org_tensorflow",
    strip_prefix = "tensorflow-2.11.0",
    urls = ["https://github.com/tensorflow/tensorflow/archive/refs/tags/v2.11.0.tar.gz"],
)

load("@org_tensorflow//tensorflow:workspace3.bzl", "tf_workspace3")

tf_workspace3()

load("@org_tensorflow//tensorflow:workspace2.bzl", "tf_workspace2")

tf_workspace2()

load("@org_tensorflow//tensorflow:workspace1.bzl", "tf_workspace1")

tf_workspace1(with_rules_cc = False)
