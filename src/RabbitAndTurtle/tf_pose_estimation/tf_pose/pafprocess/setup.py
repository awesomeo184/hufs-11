from distutils.core import setup, Extension
import numpy
import os
import numpy as np

# os.environ['CC'] = 'g++';
setup(name='pafprocess_ext', version='1.0',
    ext_modules=[
        Extension('_pafprocess', ['pafprocess.cpp', 'pafprocess.i'],
                  swig_opts=['-c++'],
                  depends=["pafprocess.h"],
                  include_dirs=[numpy.get_include(), '.'])
    ],
    py_modules=[
        "pafprocess"
    ]
)

EXT = Extension('_pafprocess',
                sources=[
                    'tf_pose/pafprocess/pafprocess_wrap.cpp',
                    'tf_pose/pafprocess/pafprocess.cpp',
                ],
                swig_opts=['-c++'],
                include_dirs=[np.get_include()])
