# -*- coding: utf-8 -*-

"""
Fabfile to deploy etc
"""
from fabric.api import *

#==============================================================================
# Configs
#==============================================================================

env.hosts = ['ojii.ch']
env.user = 'jonas'

ROOT = '/home/jonas/app/'

#==============================================================================
# Tasks    
#==============================================================================

def uname():
    run('uname -a')
    
def deploy():
    """
    Checkout the code in a new folder.
    """
    with cd(ROOT):
        run('git pull origin master')
        run('env/bin/pip install -r requirements.txt')
        restart()

def restart():
    run('sudo supervisorctl restart ojiich-gunicorn')
