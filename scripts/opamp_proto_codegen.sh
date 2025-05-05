#!/bin/bash
#
# Regenerate python code from opamp protos in
# https://github.com/open-telemetry/opamp-spec
#
# To use, update OPAMP_SPEC_REPO_BRANCH_OR_COMMIT variable below to a commit hash or
# tag in opentelemtry-proto repo that you want to build off of. Then, just run
# this script to update the proto files. Commit the changes as well as any
# fixes needed in the OTLP exporter.
#
# Optional envars:
#   OPAMP_SPEC_REPO_DIR - the path to an existing checkout of the opamp-spec repo

# Pinned commit/branch/tag for the current version used in the opamp python package.
OPAMP_SPEC_REPO_BRANCH_OR_COMMIT="v0.12.0"

set -e

OPAMP_SPEC_REPO_DIR=${OPAMP_SPEC_REPO_DIR:-"/tmp/opamp-spec"}
# root of opentelemetry-python repo
repo_root="$(git rev-parse --show-toplevel)"
venv_dir="/tmp/opamp_proto_codegen_venv"

# run on exit even if crash
cleanup() {
    echo "Deleting $venv_dir"
    rm -rf $venv_dir
}
trap cleanup EXIT

echo "Creating temporary virtualenv at $venv_dir using $(python3 --version)"
python3 -m venv $venv_dir
source $venv_dir/bin/activate
python -m pip install \
    -c $repo_root/opamp-gen-requirements.txt \
    grpcio-tools mypy-protobuf
echo 'python -m grpc_tools.protoc --version'
python -m grpc_tools.protoc --version

# Clone the proto repo if it doesn't exist
if [ ! -d "$OPAMP_SPEC_REPO_DIR" ]; then
    git clone https://github.com/open-telemetry/opamp-spec.git $OPAMP_SPEC_REPO_DIR
fi

# Pull in changes and switch to requested branch
(
    cd $OPAMP_SPEC_REPO_DIR
    git fetch --all
    git checkout $OPAMP_SPEC_REPO_BRANCH_OR_COMMIT
    # pull if OPAMP_SPEC_BRANCH_OR_COMMIT is not a detached head
    git symbolic-ref -q HEAD && git pull --ff-only || true
)

cd $repo_root/src/elasticotel/opamp/proto

# clean up old generated code
find . -regex ".*_pb2.*\.pyi?" -exec rm {} +

# generate proto code for all protos
all_protos=$(find $OPAMP_SPEC_REPO_DIR/ -name "*.proto")
python -m grpc_tools.protoc \
    -I $OPAMP_SPEC_REPO_DIR/proto \
    --python_out=. \
    --mypy_out=. \
    $all_protos
