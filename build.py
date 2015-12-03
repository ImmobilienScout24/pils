from pybuilder.core import use_plugin, init
from pybuilder.vcs import VCSRevision

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "pils"
version = "0.1"
default_task = "publish"
summary = "PILS - Python uTILS"
description = "PILS is a container for utilis written in python"
license = 'Apache License 2.0'
url = 'https://github.com/ImmobilienScout24/pils'


@init
def set_properties(project):
    project.depends_on("boto3")
    project.build_depends_on("mock")


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.version = '%s.%s-%s' % (
        project.version, VCSRevision().get_git_revision_count(), os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['install_build_dependencies', 'publish']
    project.set_property(
        'install_dependencies_index_url', os.environ.get('PYPIPROXY_URL'))
    project.set_property('install_dependencies_use_mirrors', False)
    project.set_property('teamcity_output', True)
