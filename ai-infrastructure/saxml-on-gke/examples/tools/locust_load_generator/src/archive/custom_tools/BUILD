load("//saxml:saxml.bzl", "go_binary", "go_library")

go_library(
    name = "lib",
    srcs = ["locust_worker.go"],
    visibility = ["//visibility:private"],
    deps = [
        "//saxml/client/go:sax",
        "//saxml/common/platform:env",
        "//saxml/common/platform:register",
        "@com_github_myzhan_boomer//:boomer",
    ],
)

go_binary(
    name = "locust_worker",
    embed = [":lib"],
    visibility = ["//visibility:public"],
)
