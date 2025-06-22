from setuptools import setup, find_packages

setup(
    name='TanksMental',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy==2.2.2',
        'Panda3D==1.10.15',
        'panda3d-gltf==1.2.1',
        'panda3d-simplepbr==0.12.0',
        'pillow==11.0.0',
        'pygame==2.6.1',
        'PyOpenGL==3.1.9',
        'pyperclip==1.9.0',
        'PyTMX==3.32',
        'screeninfo==0.8.1',
        'typing_extensions==4.12.2',
        'ursina==7.0.0',
        'platformdirs>=4.2.0',
    ],
    entry_points={
        'console_scripts': [
            'tanksmental=tanksmental.main:main', 
        ],
    },
)
