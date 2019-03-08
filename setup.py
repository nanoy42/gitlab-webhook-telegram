from setuptools import setup

setup(name='gitlab-webhook-telegram',
      version='1.0',
      description='A simple bot reacting to gitlab webhook',
      url='http://github.com/nanoy42/gitlab-webhook-telegram',
      author='Yoann `Nanoy` Pietri',
      author_email='me@nanoy.fr',
      license='GNU General Public License v3.0',
      packages=['gwt'],
      zip_safe=False,
      install_requires=['docopt', 'python-telegram-bot'],
      scripts=['bin/gwt'],
      include_package_data=True,
)
