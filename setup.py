"""Setup file for eje."""


from setuptools import setup  # type: ignore


setup(
    author_email="cganterh@gmail.com",
    author="Cristóbal Ganter",
    install_requires=["setuptools>=42.0", "tornado~=6.0"],
    name="eje",
    py_modules=["eje"],
    setup_requires=["setuptools_scm"],
    url="https://github.com/cganterh/eje",
    use_scm_version=True,
)
