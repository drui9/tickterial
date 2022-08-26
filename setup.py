from setuptools import setup


def dependencies():
    release, dev = list(), list()
    release_marker = '[packages]'
    with open('Pipfile', 'r') as dfile:
        lines = dfile.read().split(release_marker)[1].split('\n')
        stop_idx = lines.index('', 1)
        for i in range(1, stop_idx):
            dep = lines[i]
            if d := dep.strip():
                release.append(d.split('=')[0])
        stop_idx += 1  # for blank line after
        for i in range(stop_idx + 1, lines.index('', stop_idx + 1)):
            dep = lines[i]
            if d := dep.strip():
                dev.append(d.split('=')[0])
    return release, dev

def readme():
   with open('README.md','r') as md:
      return md.read()

setup(
   name = 'tickterial',
   version ='2.0',
   author ='sp3rtah',
   description ='Download and cache tick data from Dukascopy Bank SA',
   long_description = readme(),
   packages=['tickterial'],
   install_requires=dependencies()[0]
)
