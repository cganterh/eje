"""Setup file for eje."""


from setuptools import setup


setup(
    author_email="cganterh@gmail.com",
    author="Cristóbal Ganter",
    install_requires=["cysystemd", "tornado"],
    name="eje",
    py_modules=["eje"],
    setup_requires=["setuptools_scm"],
    url="https://github.com/cganterh/eje",
    use_scm_version=True,
)