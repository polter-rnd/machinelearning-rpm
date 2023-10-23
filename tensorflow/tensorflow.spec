%global pkgvers 1
%global schash0 4dacf3f368eb7965e9b5c3bbdd5193986081c3b2
%global branch0 master
%global source0 https://github.com/tensorflow/tensorflow.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

%global vcu_maj 12
%global vcu_min 3

# ext libs
%define ext_flatbuf 1
%define ext_protbuf 1
%define ext_grpcdev 1

Name:           tensorflow
Version:        %(curl -s "https://raw.githubusercontent.com/tensorflow/tensorflow/%{schash0}/tensorflow/tensorflow.bzl" | grep "VERSION =" | cut -d'"' -f2 | sed 's|.[a-z,A-Z]||')
Release:        %{pkgvers}.git%{sshort0}.cu%{vcu_maj}_%{vcu_min}%{?dist}
Summary:        Tensorflow Neural Network Package
License:        BSD

URL:            https://www.tensorflow.org

ExclusiveArch:  x86_64 aarch64 ppc64le

Patch3:         tf-proto.patch
Patch4:         tensorflow-mlir.patch
Patch5:         tensorflow-aarch64.patch
Patch6:         tensorflow-ppc64le.patch
Patch7:         tensorflow-pip.patch
Patch8:         tf-py312.patch

BuildRequires:  gcc-c++ git unzip curl bazel6 python3 python3-setuptools patchelf
BuildRequires:  libicu-devel pcre-devel libjpeg-turbo-devel libpng-devel giflib-devel
BuildRequires:  python3-devel sqlite-devel double-conversion-devel libcurl-devel abseil-cpp-devel
BuildRequires:  python3dist(cython) python3dist(wheel) python3dist(wrapt) python3dist(six)
BuildRequires:  python3dist(packaging) python3dist(requests) python3dist(typing-extensions)
BuildRequires:  python3dist(opt-einsum) python3dist(dill) python3dist(gast) python3dist(absl-py)
BuildRequires:  python3dist(astor) python3dist(keras-preprocessing) python3dist(astunparse)
BuildRequires:  python3dist(flatbuffers) python3dist(protobuf) >= 3.21.9
#BuildRequires:  re2-devel snappy-devel
%if 0%{?rhel} == 8
BuildRequires:  python3dist(dataclasses)
Requires:       python3dist(dataclasses)
%endif
%if ! (0%{?rhel} == 9)
BuildRequires:  python3dist(tblib)
Requires:       python3dist(tblib)
%endif
%if %{ext_flatbuf}
BuildRequires:  flatbuffers-devel /usr/bin/flatc
%endif
%if %{ext_protbuf}
BuildRequires:  protobuf-compat-devel >= 3.21.9
%endif
%if %{ext_grpcdev}
BuildRequires:  grpc-compat grpc-compat-plugins grpc-compat-devel
#%if 0%{?rhel} == 8
#BuildRequires:  grpc-cpp
#%endif
%endif
%if ! (0%{?rhel} == 8)
BuildRequires:  libxcrypt-compat
%else
BuildRequires:  libxcrypt
%endif
Requires:       python3dist(numpy) python3dist(packaging) python3dist(requests) python3dist(termcolor)
Requires:       python3dist(six) python3dist(typing-extensions) python3dist(astor) python3dist(wrapt)
Requires:       python3dist(astunparse) python3dist(gast) python3dist(flatbuffers) python3dist(protobuf) >= 3.21.9
Requires:       python3dist(opt-einsum) python3dist(dill) python3dist(keras-preprocessing) python3dist(absl-py)
Requires:       python3dist(ml-dtypes)
Recommends:     keras
Recommends:     tensorboard
Recommends:     tensorflow-estimator
Recommends:     python3dist(tensorflow-io-gcs-filesystem)
Recommends:     python3dist(libclang)

%define have_cuda 1
%define have_tensorrt 0
%define have_cuda_gcc 1
%define gpu_target_arch "6.1,7.5,8.6,8.9,9.0,5.2"

%bcond_without cuda
%if %{without cuda}
%define have_cuda 0
%endif

%if %{have_cuda}
%if %{have_cuda_gcc}
%if (0%{?fedora} > 34) || (0%{?rhel} > 9)
BuildRequires:  cuda-gcc-c++
%endif
%endif
BuildRequires:  cuda-nvcc-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-nvtx-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-cudart-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-nvml-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-nvrtc-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-driver-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-nvprune-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-profiler-api-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-cupti-%{vcu_maj}-%{vcu_min}
BuildRequires:  cuda-profiler-api-%{vcu_maj}-%{vcu_min}
BuildRequires:  libcublas-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  libcufft-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  libcurand-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  libcusparse-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  libcusolver-devel-%{vcu_maj}-%{vcu_min}
BuildRequires:  libnccl-devel
BuildRequires:  libcudnn8-devel
Requires:       cuda-cudart-%{vcu_maj}-%{vcu_min}
Requires:       cuda-nvrtc-%{vcu_maj}-%{vcu_min}
Requires:       libcublas-%{vcu_maj}-%{vcu_min}
Requires:       libcufft-%{vcu_maj}-%{vcu_min}
Requires:       libcurand-%{vcu_maj}-%{vcu_min}
Requires:       libcusparse-%{vcu_maj}-%{vcu_min}
Requires:       libcusolver-%{vcu_maj}-%{vcu_min}
Requires:       libnvjitlink-%{vcu_maj}-%{vcu_min}
Requires:       libcudnn8
%endif

%if %{have_tensorrt}
BuildRequires:  libnvinfer-plugin-devel libnvonnxparsers-devel
%endif

%global debug_package %{nil}
%global _lto_cflags %{nil}
%undefine _hardened_build
%undefine _annotated_build

%description
Open Source Machine Learning Framework for Everyone

%package        tflite
Summary:        Libraries for tensoflow lite
Requires:       %{name} = %{version}-%{release}

%description    tflite
This package contains libraries for tensorflow lite.

%package        devel
Summary:        Development files for tensoflow
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-tflite = %{version}-%{release}

%description    devel
This package contains development files for tensorflow.


%prep
%setup -T -c %{name} -n %{name}
find %{_builddir} -name SPECPARTS -exec rm -rf {} +
git clone --depth 1 -n -b %{branch0} %{source0} %{name}
git -C %{name} fetch --depth 1 origin %{schash0}
git -C %{name} reset --hard %{schash0}
git -C %{name} log --format=fuller

pushd %{name}
pwd
%patch -P 3 -p1 -b .pbuff~
# % patch -P 4 -p1 -b .mlir~
# % patch -P 5 -p1 -b .aarch64~
# % patch -P 6 -p1 -b .ppc64le~
%patch -P 7 -p1 -b .pip~
%patch -P 8 -p1 -b .py312~
popd

# no cub for cuda >= 11.x
find . -name 'BUILD' -exec sed -i '/cub_archive/d' {} +
sed -i 's|third_party/cub/|cub/|g' tensorflow/tensorflow/core/kernels/gpu_prim.h
# cudart versioning
sed -i '/"cupti": /,/static/s/cuda_config.cuda_version/version = None/g' tensorflow/third_party/gpus/cuda_configure.bzl
sed -i '/"cudart": /,/static/s/cuda_config.cuda_version/version = None/g' tensorflow/third_party/gpus/cuda_configure.bzl
sed -i '/"cusolver": /,/static/s/cuda_config.cusolver_version/version = None/g' tensorflow/third_party/gpus/cuda_configure.bzl
# python >= 3.10
sed -i 's|from distutils import sysconfig|import sysconfig|' tensorflow/third_party/py/python_configure.bzl
sed -i 's|print(sysconfig.get_python_inc())|print(sysconfig.get_paths()[\\\"include\\\"])|' tensorflow/third_party/py/python_configure.bzl
# buildsys python3 shebang
sed -i 's|name = "py3_runtime",|name = "py3_runtime",\n    stub_shebang = "#!/usr/bin/env python3",|' tensorflow/third_party/py/BUILD.tpl
# other python3 shebang
sed -i 's|python|python3|' tensorflow/tensorflow/lite/tools/visualize.py
sed -i 's|python|python3|' tensorflow/tensorflow/tools/ci_build/builds/check_system_libs.py
sed -i 's|python|python3|' tensorflow/third_party/gpus/crosstool/clang/bin/crosstool_wrapper_driver_is_not_gcc.tpl
sed -i 's|python|python3|' tensorflow/third_party/gpus/crosstool/clang/bin/crosstool_wrapper_driver_rocm.tpl
sed -i 's|python|python3|' tensorflow/third_party/gpus/crosstool/windows/msvc_wrapper_for_nvcc.py.tpl
# protobuf missings
sed -i 's|-lprotoc|%{_libdir}/libstdc++.so.6 -lprotoc|' tensorflow/third_party/systemlibs/protobuf.BUILD
sed -i 's|-lprotobuf|%{_libdir}/libstdc++.so.6 -lprotobuf|' tensorflow/third_party/systemlibs/protobuf.BUILD
sed -i 's|"@com_google_protobuf//:well_known_types_py_pb2_genproto"|dep + "_genproto"|' tensorflow/tensorflow/tsl/platform/default/build_config.bzl
# license files
#sed -i '/"\/\/:LICENSE",/d' tensorflow/tensorflow/tools/pip_package/BUILD
sed -i '/"@flatbuffers\/\/:LICENSE",/d' tensorflow/tensorflow/tools/pip_package/BUILD
# regenerate schema
%if %{ext_flatbuf}
for fbs in $(find %{name} -name '*_generated.h')
do
  rm $fbs
  # proto
  if [ -f ${fbs/_generated.h}.proto ]
  then
    echo "${fbs/_generated.h}.proto"
    flatc --proto -I ./tensorflow/ \
      -o $(dirname ${fbs/_generated.h}.proto) \
      ${fbs/_generated.h}.proto
    sed -i 's/tflite.proto/tflite/' ${fbs/_generated.h}.fbs
  fi
  # flat
  if [ -f ${fbs/_generated.h}.fbs ]
  then
    echo "${fbs/_generated.h}.fbs"
    flatc --no-union-value-namespacing --gen-object-api -I %{name} \
          -o $(dirname ${fbs/_generated.h}.fbs) \
          -c ${fbs/_generated.h}.fbs
  fi
done
%endif
# py3.11
%if 0%{?fedora} >= 38
sed -i 's|return self.value.component|return self.value[1]|' %{name}/tensorflow/lite/python/convert_phase.py
%endif

%build
pushd %{name}
bazel --version | awk '{print $2}' > .bazelversion
echo 'build --host_force_python=PY3' > .tf_configure.bazelrc
echo 'build --python_path="%{python3}"' >> .tf_configure.bazelrc
echo 'build --action_env PYTHON_BIN_PATH="%{python3}"' >> .tf_configure.bazelrc
echo 'build --action_env PYTHON_LIB_PATH="%{python3_sitearch}"' >> .tf_configure.bazelrc
echo 'build --action_env PYTHONPATH="%{python3_sitelib}:%{python3_sitearch}"' >> .tf_configure.bazelrc
echo 'build --action_env TF_CONFIGURE_IOS="0"' >> .tf_configure.bazelrc
%if %{have_cuda}
echo 'build --action_env CUDA_TOOLKIT_PATH="/usr/local/cuda"' >> .tf_configure.bazelrc
echo 'build --action_env TF_CUDA_COMPUTE_CAPABILITIES=%{gpu_target_arch}' >> .tf_configure.bazelrc
%if %{have_cuda_gcc}
%if (0%{?fedora} > 34) || (0%{?rhel} > 9)
echo 'build --action_env GCC_HOST_COMPILER_PATH="%{_bindir}/cuda-gcc"' >> .tf_configure.bazelrc
%endif
%endif
%if %{have_tensorrt}
echo 'build --config=tensorrt' >> .tf_configure.bazelrc
%endif
echo 'build --config=cuda' >> .tf_configure.bazelrc
%endif
echo 'build --config=xla' >> .tf_configure.bazelrc
echo 'build:xla --define with_xla_support=true' >> .tf_configure.bazelrc
echo 'build:opt --define with_default_optimizations=true' >> .tf_configure.bazelrc
echo 'build:opt --copt=-Wp,-D_GLIBCXX_ASSERTIONS --copt=-Wno-sign-compare --copt=-Wno-error --copt=-Wno-error=array-bounds --copt=-Wno-error=stringop-overflow' >> .tf_configure.bazelrc
echo 'build:opt --cxxopt=-Wp,-D_GLIBCXX_ASSERTIONS --cxxopt=-Wno-sign-compare --cxxopt=-Wno-error --cxxopt=-Wno-error=array-bounds --cxxopt=-Wno-error=stringop-overflow' >> .tf_configure.bazelrc
%if ! (0%{?rhel} == 8)
echo 'build:opt --copt=-Wno-error=array-parameter' >> .tf_configure.bazelrc
echo 'build:opt --cxxopt=-Wno-error=array-parameter' >> .tf_configure.bazelrc
%endif
%ifarch x86_64
echo 'build:opt --copt=-mtune=generic' >> .tf_configure.bazelrc
echo 'build:opt --cxxopt=-mtune=generic' >> .tf_configure.bazelrc
echo 'build:opt --host_copt=-mtune=generic' >> .tf_configure.bazelrc
echo 'build:opt --host_cxxopt=-mtune=generic' >> .tf_configure.bazelrc
%endif
%ifarch ppc64le
echo 'build:opt --define tflite_with_xnnpack=flase' >> .tf_configure.bazelrc
echo 'build:opt --copt=-mcpu=power8 --copt=-mtune=power8' >> .tf_configure.bazelrc
echo 'build:opt --cxxopt=-mcpu=power8 --cxxopt=-mtune=power8' >> .tf_configure.bazelrc
echo 'build:opt --host_copt=-mcpu=power8 --host_copt=-mtune=power8' >> .tf_configure.bazelrc
echo 'build:opt --host_cxxopt=-mcpu=power8 --host_cxxopt=-mtune=power8' >> .tf_configure.bazelrc
%endif
echo 'test --flaky_test_attempts=3' >> .tf_configure.bazelrc
echo 'test --test_size_filters=small,medium' >> .tf_configure.bazelrc
echo 'test:v1 --test_tag_filters=-benchmark-test,-no_oss,-gpu,-oss_serial' >> .tf_configure.bazelrc
echo 'test:v1 --build_tag_filters=-benchmark-test,-no_oss,-gpu' >> .tf_configure.bazelrc
echo 'test:v2 --test_tag_filters=-benchmark-test,-no_oss,-gpu,-oss_serial,-v1only' >> .tf_configure.bazelrc
echo 'test:v2 --build_tag_filters=-benchmark-test,-no_oss,-gpu,-v1only' >> .tf_configure.bazelrc

# system libs
export LOCAL_LIBS="curl,zlib,gif,png,libjpeg_turbo,icu,org_sqlite,cython,six_archive,org_sqlite,double_conversion,typing_extensions_archive,astor_archive,wrapt,astunparse_archive,opt_einsum_archive,absl_py,dill_archive,gast_archive"
#export LOCAL_LIBS="$LOCAL_LIBS,llvm-project,flatbuffers,com_google_absl,com_googlesource_code_re2,snappy,com_github_grpc_grpc,com_google_protobuf"
%if %{ext_flatbuf}
export LOCAL_LIBS="$LOCAL_LIBS,flatbuffers"
%endif
%if %{ext_protbuf}
export LOCAL_LIBS="$LOCAL_LIBS,com_google_protobuf"
%endif
%if %{ext_grpcdev}
export LOCAL_LIBS="$LOCAL_LIBS,com_github_grpc_grpc"
%endif
%if ! (0%{?rhel} == 9)
export LOCAL_LIBS="$LOCAL_LIBS,tblib_archive"
%endif
%ifarch aarch64
export BAZEL_JAVAC_OPTS="-J-Xmx4g -J-Xms512m"
%endif

export TMP=/tmp
export TF_NEED_AWS=0
export TF_SYSTEM_LIBS=$LOCAL_LIBS
export TF_IGNORE_MAX_BAZEL_VERSION=1
export TEST_TMPDIR="%{_builddir}/%{name}"
export LD_LIBRARY_PATH="/usr/local/cuda-%{vcu_maj}.%{vcu_min}/%{_lib}/"
%if 0%{?fedora} >= 38
export TF_PYTHON_VERSION=3.11
%else
export TF_PYTHON_VERSION=3.9
%endif

bazel build \
    --config=opt \
    --config=v2 \
    --config=cuda \
    --config=noaws \
    --config=nohdfs \
    --define=no_tensorflow_py_deps=true \
    --action_env TF_SYSTEM_LIBS=$LOCAL_LIBS \
    --subcommands \
    --explain=build.log \
    --show_result=2147483647 \
    --local_ram_resources=HOST_RAM*.75 \
    --jobs %{_smp_build_ncpus} \
    --verbose_failures \
    --incompatible_use_python_toolchains \
    //tensorflow/tools/pip_package:build_pip_package

bazel build \
    --config=opt \
    --config=v2 \
    --config=cuda \
    --config=noaws \
    --config=nohdfs \
    --define=no_tensorflow_py_deps=true \
    --action_env TF_SYSTEM_LIBS=$LOCAL_LIBS \
    --subcommands \
    --explain=build-tflite.log \
    --show_result=2147483647 \
    --local_ram_resources=HOST_RAM*.75 \
    --jobs %{_smp_build_ncpus} \
    --verbose_failures \
    //tensorflow/lite:libtensorflowlite.so

bazel build \
    --config=opt \
    --config=v2 \
    --config=cuda \
    --config=noaws \
    --config=nohdfs \
    --define=no_tensorflow_py_deps=true \
    --action_env TF_SYSTEM_LIBS=$LOCAL_LIBS \
    --subcommands \
    --explain=build-tflite_c.log \
    --show_result=2147483647 \
    --local_ram_resources=HOST_RAM*.75 \
    --jobs %{_smp_build_ncpus} \
    --verbose_failures \
    //tensorflow/lite/c:libtensorflowlite_c.so

popd


%install
pushd %{name}

export PYTHON_BIN_PATH=%{python3}
export LD_LIBRARY_PATH="/usr/local/cuda-%{vcu_maj}.%{vcu_min}/%{_lib}/"

bash ./bazel-bin/tensorflow/tools/pip_package/build_pip_package %{buildroot}/%{python3_sitearch}/
unzip %{buildroot}/%{python3_sitearch}/*.whl -d %{buildroot}/%{python3_sitearch}/
rm -rf %{buildroot}/%{python3_sitearch}/*.whl
rm -rf %{buildroot}/%{python3_sitearch}/*.data

# remove weak depends
sed -i '/Requires-Dist: /d' %{buildroot}/%{python3_sitearch}/*.dist-info/METADATA

# fix chmod
find %{buildroot}/%{python3_sitearch}/ -type f -exec chmod 644 {} \;

# strip libraries
find %{buildroot}/%{python3_sitearch}/ -name "*.so*" -exec strip {} \;
find %{buildroot}/%{python3_sitearch}/ -name "*.so*" -exec chmod 755 {} \;

mv -f %{buildroot}/%{python3_sitearch}/tensorflow/libtensorflow_framework.so.2 \
      %{buildroot}/%{_libdir}/libtensorflow_framework.so.2
ln -sf %{_libdir}/libtensorflow_framework.so.2 \
       %{buildroot}/%{python3_sitearch}/tensorflow/libtensorflow_framework.so.2
ln -sf %{_libdir}/libtensorflow_framework.so.2 \
       %{buildroot}/%{_libdir}/libtensorflow_framework.so \

# tflite
install -m755 bazel-bin/tensorflow/lite/libtensorflowlite.so %{buildroot}/%{_libdir}/
install -m755 bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so %{buildroot}/%{_libdir}/

# include dirs
mkdir -p %{buildroot}/%{_includedir}
ln -sf %{python3_sitearch}/%{name}/include/%{name} \
       %{buildroot}/%{_includedir}/%{name}

# tflite additional headers
for f in `find %{name}/lite/ -name '*.h'`
do
  install -D -pm 644 $f %{buildroot}/%{python3_sitearch}/%{name}/include/$f
done

# clean external includes
for d in `ls %{buildroot}/%{python3_sitearch}/%{name}/include/ | grep -v %{name}`
do
  rm -rf %{buildroot}/%{python3_sitearch}/%{name}/include/$d
done

popd

# cleanup bad ro build rights
chmod +w -R %{_builddir}/%{name}/_bazel*


%files
%license %{name}/LICENSE
%doc %{name}/README.md
%doc %{name}/CONTRIBUTING.md
%exclude %{_libdir}/libtensorflowlite.so
%exclude %{_libdir}/libtensorflowlite_c.so
%{_libdir}/*.so*
%exclude %{python3_sitearch}/%{name}/include
%{python3_sitearch}/*

%files tflite
%license %{name}/LICENSE
%{_libdir}/libtensorflowlite.so
%{_libdir}/libtensorflowlite_c.so

%files devel
%license %{name}/LICENSE
%{_includedir}/%{name}
%{python3_sitearch}/%{name}/include


%changelog
* Sun Oct 22 2023 Pavel Artsishevskii <polter.rnd@gmail.com>
- update to 2.14

* Wed Dec 04 2019 Balint Cristian <cristian.balint@gmail.com>
- github upstream releases
