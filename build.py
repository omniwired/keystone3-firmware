# -*- coding: utf-8 -*-
# !/usr/bin/python

import shutil
import platform
import subprocess
import argparse
import os

source_path = os.path.dirname(os.path.abspath(__file__))
build_dir = "build"
build_path = source_path + '/' + build_dir

argParser = argparse.ArgumentParser()
argParser.add_argument("-e", "--environment", help="please specific which enviroment you are building, dev or production")
argParser.add_argument("-p", "--purpose", help="please specific what purpose you are building, set it to `debug` for building unsigned firmware.")

def build_firmware(environment):
    is_release = environment == "production"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    padding_script = os.path.join(build_dir, "padding_bin_file.py")
    if not os.path.exists(padding_script):
        shutil.copy(os.path.join("tools/padding_bin_file", "padding_bin_file.py"), build_dir)

    os.chdir(build_path)

    if platform.system() == 'Darwin':
        cmd = 'cmake -G "Unix Makefiles" .. -DLIB_RUST_C=ON -DCMAKE_C_COMPILER=/usr/bin/clang -DCMAKE_CXX_COMPILER=/usr/bin/clang++'
    else:
        cmd = 'cmake -G "Unix Makefiles" .. -DLIB_RUST_C=ON'
    if is_release:
        cmd += ' -DBUILD_PRODUCTION=true'
    cmd_result = os.system(cmd)
    if cmd_result != 0:
        return cmd_result
    make_result = os.system('make -j')
    if make_result != 0:
        return make_result
    return os.system('python padding_bin_file.py mh1903.bin')


def ota_maker():
    os.chdir(source_path)
    if platform.system() == 'Darwin':
        args = ("./tools/mac/ota-maker", "--source", "./build/mh1903.bin", "--destination", "./build/keystone3.bin")
    else:
        args = ("./tools/ubuntu/ota-maker", "--source", "./build/mh1903.bin", "--destination", "./build/keystone3.bin")
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()


if __name__ == '__main__':
    args = argParser.parse_args()
    print("=============================================")
    print("--")
    print(f"Building firmware for { args.environment if args.environment else 'dev'}")
    print("--")
    print("=============================================")
    env = args.environment
    shutil.rmtree(build_path, ignore_errors=True)
    build_result = build_firmware(env)
    if build_result != 0:
        exit(1)
    if platform.system() == 'Darwin':
        ota_maker()
    purpose = args.purpose
    if purpose and purpose == "debug":
        ota_maker()