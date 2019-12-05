# coding=utf-8
import os
import sys
import subprocess
import shutil


COMMANDS_LIST = ('testmanage', 'test', 'release')
COMMANDS_INFO = {
    'testmanage': 'run manage for test project',
    'test': 'run tests (eq. "testmanage test")',
    'release': 'make distributive and upload to pypi (setup.py bdist_wheel upload)'
}


def testmanage(*args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testprj.settings")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testprj'))
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py'] + list(args))


def test(*args):
    testmanage('test', *args)


def release(*args):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    shutil.rmtree(os.path.join(root_dir, 'build'), ignore_errors=True)
    shutil.rmtree(os.path.join(root_dir, 'dist'), ignore_errors=True)
    shutil.rmtree(os.path.join(root_dir, 'django_mjml.egg-info'), ignore_errors=True)
    subprocess.call(['python', 'setup.py', 'sdist', 'bdist_wheel'])
    subprocess.call(['twine', 'upload', 'dist/*'])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in COMMANDS_LIST:
        locals()[sys.argv[1]](*sys.argv[2:])
    else:
        print('Available commands:')
        for c in COMMANDS_LIST:
            print(c + ' - ' + COMMANDS_INFO[c])
