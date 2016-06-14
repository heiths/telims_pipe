# To Use:

Download and unzip the repo.
Place userSetup.py in the scripts folder.

On first launch of Maya a dialog will pop-up, click browse. Search for wherever you unzipped abc_pipe, click save.
Two new menus will appear (ABC, Comet).

You won't need to do this step anymore.

The following guides are for use inside the repo. If you just want to use the tools, simply use the 'ABC' menu.

## To Use Maya Logger:
~~~ python
import abc_pipe
from pipe_utils import maya_logger

# launches terminal
logger = maya_logger.main()

warning = logger.warning("This is a warning")
error = logger.error("This is an error")
info = logger.info("This is some info")
debug = logger.debug("This is a debug option")
~~~
## To Use Joint Renamer:
~~~ python
import abc_pipe
from pipe_ui import joint_renamer_ui

joint_renamer = joint_renamer_ui.JointRenamer()
~~~
## To Use Curve Joint Generator:
~~~ python
import abc_pipe
from rig_tools import curve_joint_generator

gui = curve_joint_generator.CurveJointGenerator()
args = (False, 20, False, True, "testing", "r", "arm")
no_gui = curve_joint_generator.CurveJointGenerator(*args)
~~~
### reloading
~~~ python
# for reloading, just reload abc_pipe
reload(abc_pipe)
~~~
