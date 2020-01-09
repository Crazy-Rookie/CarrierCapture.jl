using Documenter
using CarrierCapture

makedocs(
    sitename = "CarrierCapture",
    format = Documenter.HTML(
        prettyurls = get(ENV, "CI", nothing) == "true"
    ),
    modules = [CarrierCapture],
    pages = [
        "Home" => "index.md",
        "Library" => Any[
            "Public" => "lib/public.md",
            "Brooglie" => "lib/brooglie.md"
        ],
    ]
)

deploydocs(
    target = "build",
    repo   = "https://github.com/WMD-group/CarrierCapture.jl.git",
)