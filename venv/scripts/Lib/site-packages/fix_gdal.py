"""
This package implements a pain-free way to install GDAL on a Windows-based computer for use with Django. For more detail
consult the accompanying README file or the package METADATA file after installation.

Mark Foley, September 2019
"""
__version__ = '0.0.7-dev0'


def fix():
    import os
    if os.name != "nt":
        print("\n", "*" * 80, "\n", "You are not running MS Windows so this package is not relevant to you", "\n",
              "*" * 80)
        return

    try:
        # We need to...
        # 1. Be able to find python library
        # 2. Ensure that django and gdal are installed
        from distutils.sysconfig import get_python_lib
        from django.contrib import gis
        import gdal as gd

        os.environ["PATH"] += os.pathsep + get_python_lib() + "\\osgeo"
        gdal_file = os.path.join(get_python_lib(), "django\\contrib\\gis\\gdal\\libgdal.py")

        # Figure out the version of the currently installed GDAL and make an entry to be added to the DLLs list in
        # libgdal.py
        gdal_ver = gd.VersionInfo()
        gdal_ver_major = str(int(gdal_ver) // 10 ** 6)[-1]
        gdal_ver_minor = str(int(gdal_ver) // 10 ** 4)[-1]
        gdal_ver_patch = str(int(gdal_ver) // 10 ** 2)[-1]
        gdal_ver_string = f"gdal{gdal_ver_major}{gdal_ver_minor}{gdal_ver_patch}"

        # fix to create version with zero patch, i.e. GDAL v 3.0.1 also now looks for gdal300.dll
        gdal_ver_string_nopatch = f"gdal{gdal_ver_major}{gdal_ver_minor}0"

        # Read libgdal.py and make sure that we haven't already updated it. We should update this ONCE only.
        with open(gdal_file, "r") as fh:
            fh_content = fh.read()
            if "lib_names = ['" + gdal_ver_string + "', '" + gdal_ver_string_nopatch + "', " in fh_content:
                return
        if not fh_content:
            raise AssertionError("Nothing read!")

        # Find the list of DLLs and add our GDAL version to it
        if "lib_names = [" in fh_content:
            new_content = \
                fh_content.replace("lib_names = [", "lib_names = ['" + gdal_ver_string + "', '" + gdal_ver_string_nopatch + "', ")
            print(new_content)

            # Replace libgdal.py with updated version
            with open(gdal_file, "w") as fh:
                fh.write(new_content)

    except Exception as e:
        message = f"Something went wrong!\n {e}\n" + \
                  f" If you can't find a module such as django or gdal, make sure that this is installed."
        print("\n", "*" * 90, "\n", message, "\n", "*" * 90)


if __name__ == "__main__":
    fix()
