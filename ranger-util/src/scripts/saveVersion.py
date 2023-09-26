# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This file is used to generate the package-info.java class that
# records the version, revision, branch, user, timestamp, and url

import os
import re
import sys
import errno
import shlex
import hashlib
from os import listdir
import locale
import datetime
import getpass
import socket
import subprocess
from subprocess import Popen,PIPE,CalledProcessError
from time import gmtime, strftime
import platform

def isWindowsSystem():
	return 'Windows' in platform.system()

def check_output(query):
	try:
		output = subprocess.check_output(query, universal_newlines=True)
		return output
	except CalledProcessError:
		# Not a git repository, or no git is installed
		return ''

def hashfile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.hexdigest()

def main():
	LANG=None
	LC_CTYPE=None
	LC_TIME=None
	version = sys.argv[1]
	shortversion = sys.argv[2]
	src_dir = os.path.join(sys.argv[3])
	revision = ""
	user = getpass.getuser()
	date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	dir = os.getcwd()
	cwd = dir.strip('scripts')
	cwd = os.path.join(cwd, "src")
	if isWindowsSystem():
		cwd = cwd.replace("\\", "/")

	if revision == "" :
		query = (["git","rev-parse","HEAD"])
		output = check_output(query)
		if output != "" :
			revision = output
			hostname = socket.gethostname()
			arr = (["git","rev-parse", "--abbrev-ref", "HEAD"])
			branch = check_output(arr)
			branch = branch.strip("* ")
			url = "git://%s/%s" % (hostname,cwd)
		else:
			revision="Unknown"
			branch="Unknown"
			url="file://cwd"

	if branch == "":
		branch="Unknown"
	if url == "":
		url="file://cwd"

	c = []
	fileList = []
	sortedList = []
	parent_dir = os.path.join(src_dir, os.pardir)

	for (dir, _, files) in os.walk(parent_dir):
		for f in files:
			path = os.path.join(dir, f)
			if path.endswith(".java"):
				if os.path.exists(path):
					fileList.append(path)
			else:
				pass

	sortedList = sorted(fileList, key = lambda x: x[:-4])
	for _, val in enumerate(sortedList):
		m = hashfile(open(val,'rb'), hashlib.sha512())
		f = m +"  "+ val + "\n"
		c.append(f)

	srcChecksum = hashlib.sha512(''.join(c).encode('UTF-8')).hexdigest()
	print(('hash of the ' + str(len(sortedList)) + '\n\t file from: ' + parent_dir + '\n\t is ' + srcChecksum))

	dir = os.path.join(src_dir,"target","gen","org","apache","ranger","common")
	if not os.path.exists(dir):
		os.makedirs(dir)

	# In Windows, all the following string ends with \r, need to get rid of them
	branch = branch.strip('\n\r')
	user = user.strip('\n\r')
	date = date.strip('\n\r')
	url = url.strip('\n\r')
	revision = revision.strip('\n\r')
	srcChecksum = srcChecksum.strip('\n\r')

	content = """/*
	 * Licensed to the Apache Software Foundation (ASF) under one
	 * or more contributor license agreements.  See the NOTICE file
	 * distributed with this work for additional information
	 * regarding copyright ownership.  The ASF licenses this file
	 * to you under the Apache License, Version 2.0 (the
	 * "License"); you may not use this file except in compliance
	 * with the License.  You may obtain a copy of the License at
	 *
	 *     http://www.apache.org/licenses/LICENSE-2.0
	 *
	 * Unless required by applicable law or agreed to in writing, software
	 * distributed under the License is distributed on an "AS IS" BASIS,
	 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	 * See the License for the specific language governing permissions and
	 * limitations under the License.
	 */
	 /*
	 * Generated by saveVersion.py
	 */
	 @RangerVersionAnnotation(version="{VERSION}", shortVersion="{SHORTVERSION}",revision="{REV}",branch="{BRANCH}", user="{USER}",date="{DATE}", url="{URL}",srcChecksum="{SRCCHECKSUM}")
							package org.apache.ranger.common;"""

	content = content.format(VERSION=version,SHORTVERSION=shortversion,USER=user,DATE=date,URL=url,REV=revision,BRANCH=branch,SRCCHECKSUM=srcChecksum)
	des = os.path.join(dir, "package-info.java")
	f = open(des , 'w')
	f.write(content)
	f.close()

main()
